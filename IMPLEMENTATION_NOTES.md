# Implementation Notes

## Assignment Requirements Checklist

✅ **GitHub GraphQL API Integration**
- Uses GitHub's GraphQL API to fetch repository data
- Implements proper query structure with pagination support

✅ **Rate Limiting**
- Respects GitHub's rate limits (5000 points/hour for authenticated requests)
- Implements intelligent rate limiting with automatic waiting
- Tracks rate limit usage to prevent exceeding limits

✅ **Retry Mechanisms**
- Uses `tenacity` library for exponential backoff retry logic
- Handles transient failures gracefully
- Specific handling for rate limit errors

✅ **PostgreSQL Storage**
- Stores crawled data in PostgreSQL database
- Flexible schema designed for future extensibility
- Efficient update operations using `ON CONFLICT`

✅ **Database Schema**
- `repositories` table for core repository information
- `repository_stars` table for historical star count tracking
- Proper indexes for efficient queries
- View for latest star counts

✅ **GitHub Actions Pipeline**
- Postgres service container configured
- Setup and dependency installation steps
- Database schema creation step
- Crawl-stars step using GitHub API
- Database dump and artifact upload steps
- Works with default GitHub token (no secrets required)

✅ **Scalability Considerations**
- Documented approach for scaling to 500 million repositories
- Distributed architecture recommendations
- Database optimization strategies
- Caching and incremental update strategies

✅ **Schema Evolution**
- Documented how schema would evolve for issues, PRs, commits, comments, reviews, CI checks
- Efficient update strategies to minimize affected rows
- Example: PR with 10 comments today, 20 tomorrow → only 10 new rows inserted

✅ **Clean Architecture**
- Separation of concerns (API, database, business logic)
- Anti-corruption layer (GitHubClient abstracts API)
- Immutability (frozen dataclasses)
- Dependency injection

## Key Features

### 1. Efficient Database Operations

- **Bulk Inserts**: Uses `executemany` for batch operations
- **Upsert Pattern**: Uses `ON CONFLICT` for efficient updates
- **Historical Tracking**: Separate table for star counts allows tracking over time
- **Indexes**: Strategic indexes on frequently queried columns

### 2. Rate Limit Management

- Tracks rate limit usage internally
- Automatically waits when approaching limits
- Provides status information for monitoring
- Handles rate limit errors gracefully

### 3. Error Handling

- Retry logic with exponential backoff
- Continues crawling even if individual requests fail
- Logs errors for debugging
- Graceful degradation

### 4. Code Quality

- Type hints throughout
- Immutable data models
- Clear separation of concerns
- Comprehensive documentation

## Running the Crawler

### Local Development

1. Set up PostgreSQL database
2. Set environment variables:
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost:5432/github_crawler
   export GITHUB_TOKEN=your_token_here
   ```
3. Run setup:
   ```bash
   python scripts/setup_db.py
   ```
4. Run crawler:
   ```bash
   python scripts/crawl_stars.py
   ```
5. Dump data:
   ```bash
   python scripts/dump_db.py
   ```

### GitHub Actions

The workflow automatically:
1. Sets up PostgreSQL service container
2. Installs dependencies
3. Creates database schema
4. Crawls 100,000 repositories
5. Dumps database to CSV/JSON
6. Uploads artifacts

**Note**: The workflow uses `GITHUB_TOKEN` which is automatically available in GitHub Actions. No additional secrets are required.

## Performance Considerations

- **Batch Size**: Processes repositories in batches of 100 (GitHub's max per query)
- **Concurrent Requests**: Single-threaded to respect rate limits (can be parallelized with multiple tokens)
- **Database Writes**: Bulk operations for efficiency
- **Query Optimization**: Uses indexes and views for fast queries

## Future Enhancements

1. **Parallel Processing**: Use multiple GitHub tokens for parallel crawling
2. **Incremental Updates**: Only crawl changed repositories
3. **Webhook Integration**: Real-time updates via GitHub webhooks
4. **Monitoring**: Add metrics and alerting
5. **Caching**: Add Redis for frequently accessed data

## Testing

While not included in this implementation, the architecture supports:
- Unit testing of individual components
- Integration testing with test database
- Mocking of GitHub API for testing
- Testing of rate limiting logic

## Known Limitations

1. **Single Token**: Currently uses one GitHub token (can be extended to token pool)
2. **Sequential Processing**: Processes requests sequentially (can be parallelized)
3. **Full Crawl**: Always does full crawl (can be made incremental)
4. **No Monitoring**: Basic logging only (can add metrics/alerting)

These limitations are acceptable for the 100,000 repository requirement but would need to be addressed for 500 million repositories.

