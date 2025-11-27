"""Database schema definitions"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Repository:
    """Immutable repository data model"""
    id: str
    name: str
    owner: str
    full_name: str
    description: Optional[str]
    url: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    pushed_at: Optional[datetime]
    language: Optional[str]
    is_private: bool
    is_fork: bool
    is_archived: bool
    
    @classmethod
    def from_github_data(cls, data: dict) -> "Repository":
        """Create Repository from GitHub API response"""
        return cls(
            id=str(data["id"]),
            name=data["name"],
            owner=data["owner"]["login"],
            full_name=data["nameWithOwner"],
            description=data.get("description"),
            url=data["url"],
            created_at=datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00")) if data.get("createdAt") else None,
            updated_at=datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00")) if data.get("updatedAt") else None,
            pushed_at=datetime.fromisoformat(data["pushedAt"].replace("Z", "+00:00")) if data.get("pushedAt") else None,
            language=data.get("primaryLanguage", {}).get("name") if data.get("primaryLanguage") else None,
            is_private=data.get("isPrivate", False),
            is_fork=data.get("isFork", False),
            is_archived=data.get("isArchived", False),
        )


@dataclass(frozen=True)
class RepositoryStar:
    """Immutable repository star count data model"""
    repository_id: str
    star_count: int
    crawled_at: datetime
    
    @classmethod
    def from_github_data(cls, repository_id: str, star_count: int) -> "RepositoryStar":
        """Create RepositoryStar from GitHub API response"""
        return cls(
            repository_id=repository_id,
            star_count=star_count,
            crawled_at=datetime.utcnow(),
        )

