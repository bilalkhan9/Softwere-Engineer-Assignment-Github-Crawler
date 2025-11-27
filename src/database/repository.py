"""Database repository for storing crawled data"""
from typing import List, Optional
from src.database.connection import DatabaseConnection
from src.database.schema import Repository, RepositoryStar


class RepositoryStore:
    """Handles storage of repository data"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def upsert_repository(self, repo: Repository):
        """Insert or update repository information"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO repositories (
                    id, name, owner, full_name, description, url,
                    created_at, updated_at, pushed_at, language,
                    is_private, is_fork, is_archived
                ) VALUES (
                    %(id)s, %(name)s, %(owner)s, %(full_name)s, %(description)s, %(url)s,
                    %(created_at)s, %(updated_at)s, %(pushed_at)s, %(language)s,
                    %(is_private)s, %(is_fork)s, %(is_archived)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    owner = EXCLUDED.owner,
                    full_name = EXCLUDED.full_name,
                    description = EXCLUDED.description,
                    url = EXCLUDED.url,
                    updated_at = EXCLUDED.updated_at,
                    pushed_at = EXCLUDED.pushed_at,
                    language = EXCLUDED.language,
                    is_private = EXCLUDED.is_private,
                    is_fork = EXCLUDED.is_fork,
                    is_archived = EXCLUDED.is_archived,
                    updated_at_db = CURRENT_TIMESTAMP
            """, {
                "id": repo.id,
                "name": repo.name,
                "owner": repo.owner,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.url,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "pushed_at": repo.pushed_at,
                "language": repo.language,
                "is_private": repo.is_private,
                "is_fork": repo.is_fork,
                "is_archived": repo.is_archived,
            })
    
    def insert_star_count(self, star: RepositoryStar):
        """Insert star count (allows historical tracking)"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO repository_stars (repository_id, star_count, crawled_at)
                VALUES (%(repository_id)s, %(star_count)s, %(crawled_at)s)
                ON CONFLICT (repository_id, crawled_at) DO NOTHING
            """, {
                "repository_id": star.repository_id,
                "star_count": star.star_count,
                "crawled_at": star.crawled_at,
            })
    
    def bulk_upsert_repositories(self, repos: List[Repository]):
        """Bulk insert/update repositories for efficiency"""
        if not repos:
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Use executemany for bulk operations
                cursor.executemany("""
                    INSERT INTO repositories (
                        id, name, owner, full_name, description, url,
                        created_at, updated_at, pushed_at, language,
                        is_private, is_fork, is_archived
                    ) VALUES (
                        %(id)s, %(name)s, %(owner)s, %(full_name)s, %(description)s, %(url)s,
                        %(created_at)s, %(updated_at)s, %(pushed_at)s, %(language)s,
                        %(is_private)s, %(is_fork)s, %(is_archived)s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        owner = EXCLUDED.owner,
                        full_name = EXCLUDED.full_name,
                        description = EXCLUDED.description,
                        url = EXCLUDED.url,
                        updated_at = EXCLUDED.updated_at,
                        pushed_at = EXCLUDED.pushed_at,
                        language = EXCLUDED.language,
                        is_private = EXCLUDED.is_private,
                        is_fork = EXCLUDED.is_fork,
                        is_archived = EXCLUDED.is_archived,
                        updated_at_db = CURRENT_TIMESTAMP
                """, [{
                    "id": repo.id,
                    "name": repo.name,
                    "owner": repo.owner,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.url,
                    "created_at": repo.created_at,
                    "updated_at": repo.updated_at,
                    "pushed_at": repo.pushed_at,
                    "language": repo.language,
                    "is_private": repo.is_private,
                    "is_fork": repo.is_fork,
                    "is_archived": repo.is_archived,
                } for repo in repos])
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def bulk_insert_star_counts(self, stars: List[RepositoryStar]):
        """Bulk insert star counts for efficiency"""
        if not stars:
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany("""
                    INSERT INTO repository_stars (repository_id, star_count, crawled_at)
                    VALUES (%(repository_id)s, %(star_count)s, %(crawled_at)s)
                    ON CONFLICT (repository_id, crawled_at) DO NOTHING
                """, [{
                    "repository_id": star.repository_id,
                    "star_count": star.star_count,
                    "crawled_at": star.crawled_at,
                } for star in stars])
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def get_repository_count(self) -> int:
        """Get total number of repositories in database"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM repositories")
            result = cursor.fetchone()
            return result["count"] if result else 0

