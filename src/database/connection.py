"""Database connection management"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
from contextlib import contextmanager
from src.config import Config


class DatabaseConnection:
    """Manages PostgreSQL database connections"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or Config.DATABASE_URL
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursors"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
            finally:
                cursor.close()

