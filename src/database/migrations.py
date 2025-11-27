"""Database schema migrations"""
from src.database.connection import DatabaseConnection


class SchemaMigration:
    """Manages database schema creation and updates"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create_schema(self):
        """Create all database tables and indexes"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Create repositories table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS repositories (
                        id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        owner VARCHAR(255) NOT NULL,
                        full_name VARCHAR(512) NOT NULL UNIQUE,
                        description TEXT,
                        url TEXT NOT NULL,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        pushed_at TIMESTAMP,
                        language VARCHAR(100),
                        is_private BOOLEAN DEFAULT FALSE,
                        is_fork BOOLEAN DEFAULT FALSE,
                        is_archived BOOLEAN DEFAULT FALSE,
                        created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create repository_stars table for historical tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS repository_stars (
                        id SERIAL PRIMARY KEY,
                        repository_id VARCHAR(255) NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                        star_count INTEGER NOT NULL,
                        crawled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(repository_id, crawled_at)
                    )
                """)
                
                # Create indexes for efficient queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_repositories_full_name 
                    ON repositories(full_name)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_repositories_owner 
                    ON repositories(owner)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_repository_stars_repo_id 
                    ON repository_stars(repository_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_repository_stars_crawled_at 
                    ON repository_stars(crawled_at DESC)
                """)
                
                # Create a view for latest star counts (efficient for queries)
                cursor.execute("""
                    CREATE OR REPLACE VIEW latest_repository_stars AS
                    SELECT DISTINCT ON (repository_id)
                        repository_id,
                        star_count,
                        crawled_at
                    FROM repository_stars
                    ORDER BY repository_id, crawled_at DESC
                """)
                
                conn.commit()
                print("Database schema created successfully")
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def create_future_schema_tables(self):
        """
        Create tables for future metadata collection.
        This demonstrates how the schema can evolve to support:
        - Issues
        - Pull Requests
        - Commits
        - Comments
        - Reviews
        - CI Checks
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Issues table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS issues (
                        id VARCHAR(255) PRIMARY KEY,
                        repository_id VARCHAR(255) NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                        number INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        body TEXT,
                        state VARCHAR(50) NOT NULL,
                        author VARCHAR(255),
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        closed_at TIMESTAMP,
                        created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(repository_id, number)
                    )
                """)
                
                # Pull requests table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pull_requests (
                        id VARCHAR(255) PRIMARY KEY,
                        repository_id VARCHAR(255) NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                        number INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        body TEXT,
                        state VARCHAR(50) NOT NULL,
                        author VARCHAR(255),
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        merged_at TIMESTAMP,
                        created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(repository_id, number)
                    )
                """)
                
                # Comments table (for both issues and PRs)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS comments (
                        id VARCHAR(255) PRIMARY KEY,
                        repository_id VARCHAR(255) NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                        issue_id VARCHAR(255) REFERENCES issues(id) ON DELETE CASCADE,
                        pull_request_id VARCHAR(255) REFERENCES pull_requests(id) ON DELETE CASCADE,
                        body TEXT NOT NULL,
                        author VARCHAR(255),
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Commits table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS commits (
                        id VARCHAR(255) PRIMARY KEY,
                        repository_id VARCHAR(255) NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                        pull_request_id VARCHAR(255) REFERENCES pull_requests(id) ON DELETE CASCADE,
                        message TEXT NOT NULL,
                        author VARCHAR(255),
                        committed_at TIMESTAMP,
                        created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Reviews table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reviews (
                        id VARCHAR(255) PRIMARY KEY,
                        repository_id VARCHAR(255) NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                        pull_request_id VARCHAR(255) NOT NULL REFERENCES pull_requests(id) ON DELETE CASCADE,
                        state VARCHAR(50) NOT NULL,
                        author VARCHAR(255),
                        body TEXT,
                        submitted_at TIMESTAMP,
                        created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # CI checks table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ci_checks (
                        id VARCHAR(255) PRIMARY KEY,
                        repository_id VARCHAR(255) NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                        pull_request_id VARCHAR(255) REFERENCES pull_requests(id) ON DELETE CASCADE,
                        name VARCHAR(255) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        conclusion VARCHAR(50),
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for future tables
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_issues_repo_id 
                    ON issues(repository_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_pull_requests_repo_id 
                    ON pull_requests(repository_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_comments_repo_id 
                    ON comments(repository_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_commits_repo_id 
                    ON commits(repository_id)
                """)
                
                conn.commit()
                print("Future schema tables created successfully")
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()

