# GitHub Repository Crawler

A scalable GitHub repository crawler that collects repository metadata using GitHub's GraphQL API and stores it in PostgreSQL.

## Overview

This project crawls GitHub repositories to collect star counts and other metadata, storing the data in a PostgreSQL database. The solution is designed with scalability in mind and follows clean architecture principles.

## Features

- **GraphQL API Integration**: Uses GitHub's GraphQL API for efficient data retrieval
- **Rate Limiting**: Respects GitHub's rate limits with intelligent retry mechanisms
- **PostgreSQL Storage**: Flexible schema designed for future extensibility
- **GitHub Actions CI/CD**: Automated pipeline with Postgres service container
- **Clean Architecture**: Separation of concerns, anti-corruption layer, immutability

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .github/
│   └── workflows/
│       └── crawl.yml
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── connection.py
│   │   └── migrations.py
│   ├── github/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── rate_limiter.py
│   │   └── queries.py
│   └── crawler/
│       ├── __init__.py
│       └── stars_crawler.py
└── scripts/
    ├── setup_db.py
    ├── crawl_stars.py
    └── dump_db.py
```

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/github_crawler
export GITHUB_TOKEN=your_github_token
```

3. Setup database:
```bash
python scripts/setup_db.py
```

4. Run crawler:
```bash
python scripts/crawl_stars.py
```

## Database Schema

The schema is designed to be flexible and efficient for updates:

- **repositories**: Core repository information
- **repository_stars**: Star counts with timestamps for historical tracking
- Future tables can be added for issues, PRs, commits, comments, reviews, CI checks

## GitHub Actions

The workflow automatically:
1. Sets up PostgreSQL service container
2. Creates database schema
3. Crawls 100,000 repositories
4. Dumps database contents as artifacts

## Scalability Considerations

For 500 million repositories:
- Distributed crawling with multiple workers
- Batch processing and bulk inserts
- Partitioning and sharding strategies
- Caching and incremental updates
- Message queue for async processing

## Architecture

### Clean Architecture Principles

The codebase follows clean architecture principles:

1. **Separation of Concerns**: 
   - `src/github/` - External API integration (anti-corruption layer)
   - `src/database/` - Data persistence layer
   - `src/crawler/` - Business logic

2. **Immutability**: 
   - Domain models (`Repository`, `RepositoryStar`) are frozen dataclasses
   - No mutable state in domain models

3. **Anti-Corruption Layer**: 
   - `GitHubClient` abstracts GitHub API details
   - Domain models are separate from API response format

4. **Dependency Inversion**: 
   - High-level modules depend on abstractions
   - Database and API clients are injected as dependencies

## Design Decisions

### Database Schema

The schema is designed for:
- **Efficiency**: Indexes on frequently queried columns
- **Historical Tracking**: `repository_stars` table tracks star count over time
- **Future Extensibility**: Schema can easily accommodate issues, PRs, comments, etc.
- **Update Efficiency**: Uses `ON CONFLICT` for upserts, minimizing affected rows

### Rate Limiting

- Respects GitHub's rate limits (5000 points/hour for authenticated requests)
- Implements exponential backoff with retry logic
- Tracks rate limit usage to prevent exceeding limits

### Error Handling

- Retry logic with exponential backoff
- Graceful handling of rate limit errors
- Continues crawling even if individual requests fail

## Scalability

See [SCALABILITY.md](SCALABILITY.md) for detailed information on:
- Scaling to 500 million repositories
- Schema evolution for future metadata
- Update efficiency strategies

## License

MIT

