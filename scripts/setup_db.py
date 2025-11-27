#!/usr/bin/env python3
"""Setup database schema"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import DatabaseConnection
from src.database.migrations import SchemaMigration


def main():
    """Create database schema"""
    print("Setting up database schema...")
    
    try:
        db = DatabaseConnection()
        migration = SchemaMigration(db)
        migration.create_schema()
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

