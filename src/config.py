"""Configuration management"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/github_crawler"
    )
    
    # GitHub API
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_API_URL: str = "https://api.github.com/graphql"
    
    # Crawler settings
    TARGET_REPOSITORIES: int = 100_000
    BATCH_SIZE: int = 100  # Repositories per GraphQL query
    MAX_RETRIES: int = 3
    
    # Rate limiting
    # GitHub allows 5000 points per hour for authenticated requests
    # Each query costs points based on complexity
    RATE_LIMIT_POINTS_PER_HOUR: int = 5000
    RATE_LIMIT_POINTS_RESET_WINDOW: int = 3600  # seconds

