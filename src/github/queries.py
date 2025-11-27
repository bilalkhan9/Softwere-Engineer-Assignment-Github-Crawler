"""GraphQL queries for GitHub API"""

# Query to search for repositories and get their star counts
# Using search to get a diverse set of repositories
REPOSITORY_SEARCH_QUERY = """
query SearchRepositories($query: String!, $first: Int!, $after: String) {
  search(query: $query, type: REPOSITORY, first: $first, after: $after) {
    repositoryCount
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        id
        name
        nameWithOwner
        description
        url
        createdAt
        updatedAt
        pushedAt
        isPrivate
        isFork
        isArchived
        stargazerCount
        primaryLanguage {
          name
        }
        owner {
          login
        }
      }
    }
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
"""

# Alternative query to get repositories by cursor (for pagination)
REPOSITORY_QUERY = """
query GetRepositories($first: Int!, $after: String) {
  search(query: "stars:>0", type: REPOSITORY, first: $first, after: $after) {
    repositoryCount
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        id
        name
        nameWithOwner
        description
        url
        createdAt
        updatedAt
        pushedAt
        isPrivate
        isFork
        isArchived
        stargazerCount
        primaryLanguage {
          name
        }
        owner {
          login
        }
      }
    }
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
"""

