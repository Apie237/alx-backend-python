# Python Decorators - Database Operations

This project demonstrates the use of Python decorators for database operations, including logging, connection management, transaction handling, retry mechanisms, and query caching.

## Files Overview

### 1. `0-log_queries.py`
**Objective**: Create a decorator that logs database queries executed by any function.

**Features**:
- Logs SQL queries before execution
- Supports queries passed as parameters or keyword arguments
- Preserves original function behavior

**Usage**:
```python
@log_queries
def fetch_all_users(query):
    # Database operation
    pass
```

### 2. `1-with_db_connection.py`
**Objective**: Create a decorator that automatically handles opening and closing database connections.

**Features**:
- Automatically opens SQLite database connection
- Passes connection to decorated function
- Ensures connection is closed even if exceptions occur
- Uses try-finally for proper cleanup

**Usage**:
```python
@with_db_connection
def get_user_by_id(conn, user_id):
    # Database operation with provided connection
    pass
```

### 3. `2-transactional.py`
**Objective**: Create a decorator that manages database transactions by automatically committing or rolling back changes.

**Features**:
- Automatically commits successful operations
- Rolls back on any exception
- Combines with `@with_db_connection` decorator
- Ensures data consistency

**Usage**:
```python
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    # Database update operation
    pass
```

### 4. `3-retry_on_failure.py`
**Objective**: Create a decorator that retries database operations if they fail due to transient errors.

**Features**:
- Configurable number of retry attempts
- Configurable delay between retries
- Logs retry attempts
- Raises last exception if all retries fail

**Usage**:
```python
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    # Database operation with retry logic
    pass
```

### 5. `4-cache_query.py`
**Objective**: Create a decorator that caches the results of database queries to avoid redundant calls.

**Features**:
- Caches query results based on SQL query string
- Detects cache hits and misses
- Reduces database load for repeated queries
- Thread-safe caching mechanism

**Usage**:
```python
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    # Database operation with result caching
    pass
```

## Key Concepts Demonstrated

### 1. **Decorator Patterns**
- Function decorators using `@functools.wraps`
- Parameterized decorators
- Decorator stacking/chaining
- Preserving function metadata

### 2. **Database Best Practices**
- Connection management
- Transaction handling
- Error handling and recovery
- Query optimization through caching

### 3. **Error Handling**
- Graceful failure handling
- Retry mechanisms
- Proper resource cleanup
- Exception propagation

### 4. **Performance Optimization**
- Query result caching
- Connection pooling concepts
- Reduced database load
- Memory-efficient operations

## Technical Implementation Details

### Connection Management
```python
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper
```

### Transaction Management
```python
def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
    return wrapper
```

### Retry Logic
```python
def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < retries:
                        time.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator
```

### Query Caching
```python
query_cache = {}

def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        cache_key = extract_query(*args, **kwargs)
        if cache_key in query_cache:
            return query_cache[cache_key]
        result = func(conn, *args, **kwargs)
        query_cache[cache_key] = result
        return result
    return wrapper
```

## Requirements

- Python 3.x
- SQLite3 (built-in)
- `functools` module (built-in)
- `time` module (built-in)

## Usage Examples

```python
# Basic usage
@log_queries
def fetch_data(query):
    # Logs: "Executing query: SELECT * FROM users"
    pass

# Combined decorators
@with_db_connection
@transactional
@retry_on_failure(retries=3, delay=1)
@cache_query
def complex_operation(conn, query):
    # Full-featured database operation
    pass
```

## Benefits

1. **Code Reusability**: Decorators can be applied to any database function
2. **Separation of Concerns**: Business logic separated from infrastructure concerns
3. **Maintainability**: Centralized error handling and logging
4. **Performance**: Caching reduces database load
5. **Reliability**: Automatic retry and transaction management
6. **Debugging**: Query logging for troubleshooting

This project demonstrates advanced Python concepts and best practices for database operations in production environments.