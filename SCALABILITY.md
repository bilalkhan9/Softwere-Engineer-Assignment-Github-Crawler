# Scalability Considerations

## Scaling to 500 Million Repositories

If this system were to scale to collect data on 500 million repositories instead of 100,000, the following changes would be necessary:

### 1. Distributed Crawling Architecture

**Current Approach:**
- Single-threaded crawler
- Sequential API requests
- Single database instance

**Scaled Approach:**
- **Distributed Workers**: Deploy multiple crawler instances across different machines/containers
- **Message Queue**: Use a message queue (e.g., RabbitMQ, Apache Kafka) to distribute work
- **Work Partitioning**: Partition repositories by owner, language, or other criteria to avoid conflicts
- **Load Balancing**: Distribute API tokens across workers to maximize rate limit utilization

### 2. Database Optimization

**Current Approach:**
- Single PostgreSQL instance
- Standard indexes
- Direct inserts

**Scaled Approach:**
- **Database Sharding**: Partition data across multiple database instances by repository ID ranges
- **Read Replicas**: Use read replicas for querying while primary handles writes
- **Partitioning**: Use PostgreSQL table partitioning for `repository_stars` by date ranges
- **Connection Pooling**: Implement connection pooling (e.g., PgBouncer) to handle high concurrency
- **Bulk Operations**: Increase batch sizes and use COPY for bulk inserts

### 3. Caching Strategy

**Current Approach:**
- No caching
- Direct database queries

**Scaled Approach:**
- **Redis Cache**: Cache frequently accessed repository data
- **CDN**: Use CDN for serving static repository metadata
- **Query Result Caching**: Cache expensive aggregation queries
- **Rate Limit Caching**: Share rate limit state across workers using distributed cache

### 4. Incremental Updates

**Current Approach:**
- Full crawl each time
- No change detection

**Scaled Approach:**
- **Change Detection**: Use GitHub webhooks or polling to detect repository changes
- **Incremental Sync**: Only update repositories that have changed since last crawl
- **Delta Processing**: Process only new/updated repositories instead of full re-crawl
- **Event-Driven Updates**: Use GitHub Events API to track repository changes in real-time

### 5. Rate Limit Management

**Current Approach:**
- Single token
- Basic rate limiting

**Scaled Approach:**
- **Multiple Tokens**: Rotate across multiple GitHub tokens to increase rate limits
- **Token Pool**: Maintain a pool of tokens and distribute requests across them
- **Intelligent Scheduling**: Schedule requests based on token reset times
- **Backoff Strategies**: Implement exponential backoff with jitter for rate limit errors

### 6. Data Storage Optimization

**Current Approach:**
- All data in PostgreSQL
- Historical data in same table

**Scaled Approach:**
- **Time-Series Database**: Use TimescaleDB (PostgreSQL extension) for star count history
- **Cold Storage**: Archive old data to S3 or similar object storage
- **Data Compression**: Compress historical data
- **Columnar Storage**: Use columnar storage for analytics queries

### 7. Monitoring and Observability

**Current Approach:**
- Basic print statements
- No monitoring

**Scaled Approach:**
- **Metrics Collection**: Use Prometheus/Grafana for metrics
- **Distributed Tracing**: Use OpenTelemetry for request tracing
- **Alerting**: Set up alerts for rate limits, errors, and performance degradation
- **Log Aggregation**: Use ELK stack or similar for log analysis

### 8. Error Handling and Resilience

**Current Approach:**
- Basic retry logic
- Single point of failure

**Scaled Approach:**
- **Circuit Breakers**: Implement circuit breakers for API calls
- **Dead Letter Queues**: Handle permanently failed items
- **Checkpointing**: Save progress periodically to resume from failures
- **Health Checks**: Implement health checks for all components

## Schema Evolution for Future Metadata

The current schema is designed to support future expansion. Here's how it would evolve:

### Current Schema

```sql
repositories (core repository info)
repository_stars (star counts with timestamps)
```

### Future Schema Additions

#### 1. Issues Table
```sql
issues (
  id, repository_id, number, title, body, state,
  author, created_at, updated_at, closed_at
)
```
- **Update Strategy**: Use `ON CONFLICT` with `updated_at` check to only update changed issues
- **Efficiency**: Only affected rows are updated (minimal rows affected)

#### 2. Pull Requests Table
```sql
pull_requests (
  id, repository_id, number, title, body, state,
  author, created_at, updated_at, merged_at
)
```
- **Update Strategy**: Similar to issues, update only when PR changes
- **Efficiency**: Track `updated_at` to detect changes

#### 3. Comments Table
```sql
comments (
  id, repository_id, issue_id, pull_request_id,
  body, author, created_at, updated_at
)
```
- **Update Strategy**: 
  - New comments: Insert only
  - Updated comments: Use `ON CONFLICT (id) DO UPDATE` with timestamp check
- **Efficiency**: A PR with 10 comments today and 20 tomorrow only inserts 10 new rows

#### 4. Commits Table
```sql
commits (
  id, repository_id, pull_request_id,
  message, author, committed_at
)
```
- **Update Strategy**: Commits are immutable, so only inserts needed
- **Efficiency**: No updates required, only new inserts

#### 5. Reviews Table
```sql
reviews (
  id, repository_id, pull_request_id,
  state, author, body, submitted_at
)
```
- **Update Strategy**: Reviews can be updated (e.g., comment edits), use conflict resolution
- **Efficiency**: Only update if review actually changed

#### 6. CI Checks Table
```sql
ci_checks (
  id, repository_id, pull_request_id,
  name, status, conclusion, started_at, completed_at
)
```
- **Update Strategy**: CI checks change status frequently, use `ON CONFLICT` with status check
- **Efficiency**: Only update rows where status/conclusion changed

### Update Efficiency Strategies

1. **Timestamp-Based Updates**: Compare `updated_at` from API with database to detect changes
2. **Hash-Based Change Detection**: Store hash of entity data, only update if hash changed
3. **Incremental Sync**: Use GitHub's `since` parameter for APIs that support it
4. **Batch Updates**: Group updates by repository to minimize database round trips
5. **Upsert Patterns**: Use PostgreSQL's `ON CONFLICT` to handle inserts and updates in one operation

### Example: Efficient Comment Updates

```sql
-- Only inserts new comments, updates existing ones if they changed
INSERT INTO comments (id, repository_id, issue_id, body, author, created_at, updated_at)
VALUES (...)
ON CONFLICT (id) DO UPDATE SET
  body = EXCLUDED.body,
  updated_at = EXCLUDED.updated_at,
  updated_at_db = CURRENT_TIMESTAMP
WHERE comments.updated_at < EXCLUDED.updated_at;
```

This ensures:
- A PR with 10 comments today → 10 inserts
- Same PR with 20 comments tomorrow → 10 updates (existing) + 10 inserts (new)
- Total rows affected: 20 (not 30)

### Partitioning Strategy

For large-scale data, use table partitioning:

```sql
-- Partition repository_stars by month
CREATE TABLE repository_stars_2024_01 PARTITION OF repository_stars
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Partition comments by repository_id ranges
CREATE TABLE comments_part_1 PARTITION OF comments
FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```

This allows:
- Efficient querying of recent data
- Easy archival of old partitions
- Parallel processing of different partitions

