# Architecture Documentation

## Overview

This project implements a GitHub repository crawler following clean architecture principles and best practices for scalability and maintainability.

## Architecture Layers

### 1. Domain Layer (Immutable Models)

**Location**: `src/database/schema.py`

- **Repository**: Immutable dataclass representing a GitHub repository
- **RepositoryStar**: Immutable dataclass representing star count at a point in time

**Principles**:
- All models are frozen (immutable)
- Models are independent of external APIs
- Models can be created from API responses via factory methods

### 2. Infrastructure Layer

#### GitHub API Client (`src/github/`)

**Components**:
- `client.py`: GraphQL API client with retry logic
- `rate_limiter.py`: Rate limit management
- `queries.py`: GraphQL query definitions

**Responsibilities**:
- Abstract GitHub API details
- Handle rate limiting
- Implement retry logic
- Convert API responses to domain models

#### Database Layer (`src/database/`)

**Components**:
- `connection.py`: Database connection management
- `migrations.py`: Schema creation and migrations
- `repository.py`: Data access layer

**Responsibilities**:
- Manage database connections
- Define and create schema
- Provide data access methods
- Handle bulk operations efficiently

### 3. Application Layer

**Location**: `src/crawler/`

**Components**:
- `stars_crawler.py`: Main crawler logic

**Responsibilities**:
- Orchestrate crawling process
- Coordinate between GitHub client and database
- Handle business logic
- Track progress

## Design Patterns

### 1. Anti-Corruption Layer

The `GitHubClient` acts as an anti-corruption layer, isolating the domain from GitHub API specifics:

```python
# Domain model is independent of API structure
repo = Repository.from_github_data(api_response)
```

### 2. Repository Pattern

The `RepositoryStore` encapsulates database access:

```python
repository_store.upsert_repository(repo)
repository_store.insert_star_count(star)
```

### 3. Dependency Injection

Components are injected rather than created internally:

```python
crawler = StarsCrawler(
    github_client=GitHubClient(),
    repository_store=RepositoryStore(db),
    target_count=100000
)
```

### 4. Immutability

Domain models are frozen dataclasses:

```python
@dataclass(frozen=True)
class Repository:
    id: str
    name: str
    # ... other fields
```

## Data Flow

```
GitHub API → GitHubClient → Domain Models → RepositoryStore → PostgreSQL
```

1. **GitHubClient** fetches data from GitHub GraphQL API
2. **Domain Models** are created from API responses (anti-corruption)
3. **RepositoryStore** persists models to database
4. **Database** stores data with proper schema and indexes

## Error Handling

### Retry Logic

- Uses `tenacity` library for retry decorators
- Exponential backoff for transient failures
- Specific handling for rate limit errors

### Rate Limiting

- Tracks rate limit usage
- Waits automatically when limits approached
- Provides status information

## Testing Considerations

The architecture supports testing through:

1. **Dependency Injection**: Easy to mock dependencies
2. **Separation of Concerns**: Each layer can be tested independently
3. **Immutable Models**: Predictable behavior in tests

## Future Extensibility

The architecture supports adding:

1. **New Data Sources**: Add new clients following the same pattern
2. **New Domain Models**: Add models following the same immutable pattern
3. **New Storage Backends**: Implement new stores following the repository pattern
4. **New Crawlers**: Add crawlers for different metadata types

## Performance Optimizations

1. **Bulk Operations**: Use `executemany` for batch inserts
2. **Indexes**: Strategic indexes on frequently queried columns
3. **Connection Pooling**: Reuse database connections
4. **Batch Processing**: Process repositories in batches

## Security Considerations

1. **Token Management**: GitHub tokens stored in environment variables
2. **SQL Injection**: Use parameterized queries
3. **Connection Security**: Use SSL for database connections in production

