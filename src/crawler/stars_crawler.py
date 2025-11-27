"""Crawler for GitHub repository stars"""
import time
from typing import List, Optional
from src.config import Config
from src.github.client import GitHubClient, RateLimitExceededError
from src.github.rate_limiter import RateLimiter
from src.database.connection import DatabaseConnection
from src.database.repository import RepositoryStore
from src.database.schema import Repository, RepositoryStar


class StarsCrawler:
    """Crawls GitHub repositories and stores star counts"""
    
    def __init__(
        self,
        github_client: GitHubClient,
        repository_store: RepositoryStore,
        target_count: int = Config.TARGET_REPOSITORIES
    ):
        self.github_client = github_client
        self.repository_store = repository_store
        self.target_count = target_count
        self.crawled_count = 0
    
    def crawl(self) -> int:
        """
        Crawl repositories until target count is reached.
        
        Returns:
            Number of repositories crawled
        """
        print(f"Starting crawl for {self.target_count:,} repositories...")
        
        # Use different search queries to get diverse repositories
        search_queries = [
            "stars:>0",  # Any repository with stars
            "stars:>10",  # Repositories with more than 10 stars
            "stars:>100",  # Repositories with more than 100 stars
            "stars:>1000",  # Repositories with more than 1000 stars
            "language:Python stars:>0",
            "language:JavaScript stars:>0",
            "language:Java stars:>0",
            "language:Go stars:>0",
            "language:Rust stars:>0",
            "pushed:>2024-01-01 stars:>0",  # Recently active
        ]
        
        query_index = 0
        cursor = None
        
        while self.crawled_count < self.target_count:
            try:
                # Rotate through different search queries for diversity
                query = search_queries[query_index % len(search_queries)]
                
                # Fetch batch of repositories
                batch_size = min(Config.BATCH_SIZE, self.target_count - self.crawled_count)
                
                result = self.github_client.search_repositories(
                    query=query,
                    first=batch_size,
                    after=cursor
                )
                
                search_data = result.get("search", {})
                nodes = search_data.get("nodes", [])
                page_info = search_data.get("pageInfo", {})
                
                if not nodes:
                    # Try next query if current one returns no results
                    query_index += 1
                    cursor = None
                    continue
                
                # Process and store repositories
                repos, stars = self._process_repositories(nodes)
                
                if repos:
                    self.repository_store.bulk_upsert_repositories(repos)
                    self.repository_store.bulk_insert_star_counts(stars)
                    
                    self.crawled_count += len(repos)
                    print(f"Crawled {self.crawled_count:,}/{self.target_count:,} repositories "
                          f"(+{len(repos)} in this batch)")
                
                # Check if we should continue with this query
                if page_info.get("hasNextPage"):
                    cursor = page_info.get("endCursor")
                else:
                    # Move to next query
                    query_index += 1
                    cursor = None
                
                # Small delay to be respectful
                time.sleep(0.1)
                
            except RateLimitExceededError as e:
                print(f"Rate limit exceeded: {e}")
                # Rate limiter should handle waiting, but add extra buffer
                status = self.github_client.get_rate_limit_status()
                print(f"Rate limit status: {status}")
                time.sleep(60)  # Wait a minute before retrying
                
            except Exception as e:
                print(f"Error during crawl: {e}")
                # Continue with next query
                query_index += 1
                cursor = None
                time.sleep(1)
        
        print(f"Crawl completed! Total repositories crawled: {self.crawled_count:,}")
        return self.crawled_count
    
    def _process_repositories(self, nodes: List[dict]) -> tuple[List[Repository], List[RepositoryStar]]:
        """
        Process GitHub API response nodes into domain models.
        
        Args:
            nodes: List of repository nodes from GraphQL response
            
        Returns:
            Tuple of (repositories, star_counts)
        """
        repos = []
        stars = []
        
        for node in nodes:
            try:
                # Create repository model
                repo = Repository.from_github_data(node)
                repos.append(repo)
                
                # Create star count model
                star_count = node.get("stargazerCount", 0)
                star = RepositoryStar.from_github_data(repo.id, star_count)
                stars.append(star)
                
            except Exception as e:
                print(f"Error processing repository node: {e}")
                continue
        
        return repos, stars

