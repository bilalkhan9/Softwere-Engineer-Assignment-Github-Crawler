#!/usr/bin/env python3
"""Crawl GitHub repository stars"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.github.client import GitHubClient
from src.database.connection import DatabaseConnection
from src.database.repository import RepositoryStore
from src.crawler.stars_crawler import StarsCrawler


def main():
    """Main crawler entry point"""
    print("Starting GitHub repository star crawler...")
    
    # Check for GitHub token
    if not Config.GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable is required")
        print("In GitHub Actions, this is automatically provided via GITHUB_TOKEN")
        sys.exit(1)
    
    try:
        # Initialize components
        github_client = GitHubClient()
        db = DatabaseConnection()
        repository_store = RepositoryStore(db)
        
        # Create crawler
        crawler = StarsCrawler(
            github_client=github_client,
            repository_store=repository_store,
            target_count=Config.TARGET_REPOSITORIES
        )
        
        # Run crawl
        count = crawler.crawl()
        
        # Verify results
        stored_count = repository_store.get_repository_count()
        print(f"\nCrawl summary:")
        print(f"  - Repositories crawled: {count:,}")
        print(f"  - Repositories stored: {stored_count:,}")
        
        if stored_count < Config.TARGET_REPOSITORIES:
            print(f"Warning: Expected {Config.TARGET_REPOSITORIES:,} repositories, "
                  f"but only {stored_count:,} were stored")
        
    except Exception as e:
        print(f"Error during crawl: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

