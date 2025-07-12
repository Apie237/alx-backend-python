#!/usr/bin/python3
"""
Decorator that caches the results of database queries to avoid redundant calls
"""

import time
import sqlite3
import functools


def with_db_connection(func):
    """
    Decorator that opens a database connection, passes it to the function,
    and closes it afterward.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The decorated function with automatic connection handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Call the original function with the connection
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection
            conn.close()
    
    return wrapper


# Global cache dictionary
query_cache = {}


def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The decorated function with query caching
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Generate cache key from query
        cache_key = None
        
        # Look for query in kwargs
        if 'query' in kwargs:
            cache_key = kwargs['query']
        # Look for query in args
        elif args:
            for arg in args:
                if isinstance(arg, str) and ('SELECT' in arg.upper() or 'UPDATE' in arg.upper() or 'INSERT' in arg.upper() or 'DELETE' in arg.upper()):
                    cache_key = arg
                    break
        
        # If we have a cache key, check if result is cached
        if cache_key and cache_key in query_cache:
            print(f"Cache hit for query: {cache_key}")
            return query_cache[cache_key]
        
        # Execute the function and cache the result
        result = func(conn, *args, **kwargs)
        
        # Cache the result if we have a cache key
        if cache_key:
            query_cache[cache_key] = result
            print(f"Cache miss - stored result for query: {cache_key}")
        
        return result
    
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call will cache the result
    print("First call:")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Fetched {len(users)} users")
    
    # Second call will use the cached result
    print("\nSecond call:")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Fetched {len(users_again)} users")