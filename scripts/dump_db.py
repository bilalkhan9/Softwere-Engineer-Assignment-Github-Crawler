#!/usr/bin/env python3
"""Dump database contents to CSV/JSON"""
import sys
import os
import json
import csv
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import DatabaseConnection


def dump_to_csv(output_file: str = "repository_data.csv"):
    """Dump repository data to CSV"""
    print(f"Dumping database to {output_file}...")
    
    db = DatabaseConnection()
    
    with db.get_cursor() as cursor:
        # Get repositories with latest star counts
        cursor.execute("""
            SELECT 
                r.id,
                r.name,
                r.owner,
                r.full_name,
                r.description,
                r.url,
                r.language,
                r.is_private,
                r.is_fork,
                r.is_archived,
                COALESCE(lrs.star_count, 0) as star_count,
                lrs.crawled_at as last_crawled_at
            FROM repositories r
            LEFT JOIN latest_repository_stars lrs ON r.id = lrs.repository_id
            ORDER BY r.full_name
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No data to dump")
            return
        
        # Write to CSV
        fieldnames = [
            "id", "name", "owner", "full_name", "description", "url",
            "language", "is_private", "is_fork", "is_archived",
            "star_count", "last_crawled_at"
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in rows:
                writer.writerow({
                    "id": row["id"],
                    "name": row["name"],
                    "owner": row["owner"],
                    "full_name": row["full_name"],
                    "description": row["description"] or "",
                    "url": row["url"],
                    "language": row["language"] or "",
                    "is_private": row["is_private"],
                    "is_fork": row["is_fork"],
                    "is_archived": row["is_archived"],
                    "star_count": row["star_count"] or 0,
                    "last_crawled_at": row["last_crawled_at"].isoformat() if row["last_crawled_at"] else "",
                })
        
        print(f"Successfully dumped {len(rows):,} repositories to {output_file}")


def dump_to_json(output_file: str = "repository_data.json"):
    """Dump repository data to JSON"""
    print(f"Dumping database to {output_file}...")
    
    db = DatabaseConnection()
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT 
                r.id,
                r.name,
                r.owner,
                r.full_name,
                r.description,
                r.url,
                r.language,
                r.is_private,
                r.is_fork,
                r.is_archived,
                r.created_at,
                r.updated_at,
                r.pushed_at,
                COALESCE(lrs.star_count, 0) as star_count,
                lrs.crawled_at as last_crawled_at
            FROM repositories r
            LEFT JOIN latest_repository_stars lrs ON r.id = lrs.repository_id
            ORDER BY r.full_name
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No data to dump")
            return
        
        # Convert to list of dicts
        data = []
        for row in rows:
            data.append({
                "id": row["id"],
                "name": row["name"],
                "owner": row["owner"],
                "full_name": row["full_name"],
                "description": row["description"],
                "url": row["url"],
                "language": row["language"],
                "is_private": row["is_private"],
                "is_fork": row["is_fork"],
                "is_archived": row["is_archived"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                "pushed_at": row["pushed_at"].isoformat() if row["pushed_at"] else None,
                "star_count": row["star_count"] or 0,
                "last_crawled_at": row["last_crawled_at"].isoformat() if row["last_crawled_at"] else None,
            })
        
        # Write to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_repositories": len(data)
                },
                "repositories": data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully dumped {len(data):,} repositories to {output_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dump database contents")
    parser.add_argument(
        "--format",
        choices=["csv", "json", "both"],
        default="both",
        help="Output format"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for dump files"
    )
    
    args = parser.parse_args()
    
    try:
        if args.format in ["csv", "both"]:
            csv_file = os.path.join(args.output_dir, "repository_data.csv")
            dump_to_csv(csv_file)
        
        if args.format in ["json", "both"]:
            json_file = os.path.join(args.output_dir, "repository_data.json")
            dump_to_json(json_file)
        
        print("Database dump completed successfully!")
        
    except Exception as e:
        print(f"Error dumping database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

