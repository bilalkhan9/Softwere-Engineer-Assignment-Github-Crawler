"""Rate limiting for GitHub API"""
import time
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class RateLimitStatus:
    """Rate limit status information"""
    remaining: int
    reset_at: datetime
    used: int
    limit: int


class RateLimiter:
    """Manages GitHub API rate limiting"""
    
    def __init__(self, points_per_hour: int = 5000, reset_window: int = 3600):
        self.points_per_hour = points_per_hour
        self.reset_window = reset_window
        self.points_used = 0
        self.window_start = datetime.utcnow()
        self.last_request_time: Optional[datetime] = None
    
    def can_make_request(self, cost: int = 1) -> bool:
        """Check if a request can be made without exceeding rate limit"""
        self._reset_if_needed()
        return (self.points_used + cost) <= self.points_per_hour
    
    def record_request(self, cost: int = 1):
        """Record that a request was made"""
        self._reset_if_needed()
        self.points_used += cost
        self.last_request_time = datetime.utcnow()
    
    def wait_if_needed(self, cost: int = 1):
        """Wait if necessary to avoid rate limit"""
        if not self.can_make_request(cost):
            wait_time = self._calculate_wait_time()
            if wait_time > 0:
                print(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                self._reset_if_needed()
    
    def _reset_if_needed(self):
        """Reset points if window has passed"""
        now = datetime.utcnow()
        elapsed = (now - self.window_start).total_seconds()
        
        if elapsed >= self.reset_window:
            self.points_used = 0
            self.window_start = now
    
    def _calculate_wait_time(self) -> float:
        """Calculate how long to wait before next request"""
        now = datetime.utcnow()
        elapsed = (now - self.window_start).total_seconds()
        remaining = self.reset_window - elapsed
        
        if remaining > 0:
            return remaining
        return 0.0
    
    def get_status(self) -> RateLimitStatus:
        """Get current rate limit status"""
        self._reset_if_needed()
        reset_at = self.window_start + timedelta(seconds=self.reset_window)
        return RateLimitStatus(
            remaining=self.points_per_hour - self.points_used,
            reset_at=reset_at,
            used=self.points_used,
            limit=self.points_per_hour
        )

