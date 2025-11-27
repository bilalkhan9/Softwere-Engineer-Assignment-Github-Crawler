"""GitHub GraphQL API client"""
import requests
import time
from typing import Dict, List, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.config import Config
from src.github.rate_limiter import RateLimiter
from src.github.queries import REPOSITORY_SEARCH_QUERY, REPOSITORY_QUERY


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass


class RateLimitExceededError(GitHubAPIError):
    """Exception raised when rate limit is exceeded"""
    pass


class GitHubClient:
    """Client for interacting with GitHub GraphQL API"""
    
    def __init__(self, token: Optional[str] = None, rate_limiter: Optional[RateLimiter] = None):
        self.token = token or Config.GITHUB_TOKEN
        if not self.token:
            raise ValueError("GitHub token is required")
        
        self.api_url = Config.GITHUB_API_URL
        self.rate_limiter = rate_limiter or RateLimiter(
            points_per_hour=Config.RATE_LIMIT_POINTS_PER_HOUR,
            reset_window=Config.RATE_LIMIT_POINTS_RESET_WINDOW
        )
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, GitHubAPIError))
    )
    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query with retry logic and rate limiting.
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            Response data from GitHub API
        """
        # Wait if rate limit would be exceeded
        self.rate_limiter.wait_if_needed(cost=1)
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_messages = [err.get("message", "Unknown error") for err in data["errors"]]
                error_type = data["errors"][0].get("type", "UNKNOWN")
                
                if "RATE_LIMITED" in error_type or "rate limit" in " ".join(error_messages).lower():
                    raise RateLimitExceededError(f"Rate limit exceeded: {', '.join(error_messages)}")
                
                raise GitHubAPIError(f"GraphQL errors: {', '.join(error_messages)}")
            
            # Update rate limiter based on response
            if "data" in data and "rateLimit" in data.get("data", {}):
                rate_limit_info = data["data"]["rateLimit"]
                # We track rate limits manually, but this provides additional info
            
            # Record the request
            self.rate_limiter.record_request(cost=1)
            
            return data.get("data", {})
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise RateLimitExceededError("Rate limit exceeded (HTTP 403)")
            raise GitHubAPIError(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Request failed: {e}")
    
    def search_repositories(
        self, 
        query: str = "stars:>0", 
        first: int = 100, 
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for repositories using GraphQL.
        
        Args:
            query: Search query string
            first: Number of results per page
            after: Cursor for pagination
            
        Returns:
            Search results with repositories and pagination info
        """
        variables = {
            "query": query,
            "first": min(first, 100),  # GitHub max is 100
            "after": after
        }
        
        return self.execute_query(REPOSITORY_SEARCH_QUERY, variables)
    
    def get_repositories(
        self, 
        first: int = 100, 
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get repositories using default search query.
        
        Args:
            first: Number of results per page
            after: Cursor for pagination
            
        Returns:
            Repository results with pagination info
        """
        variables = {
            "first": min(first, 100),
            "after": after
        }
        
        return self.execute_query(REPOSITORY_QUERY, variables)
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        status = self.rate_limiter.get_status()
        return {
            "remaining": status.remaining,
            "used": status.used,
            "limit": status.limit,
            "reset_at": status.reset_at.isoformat()
        }

