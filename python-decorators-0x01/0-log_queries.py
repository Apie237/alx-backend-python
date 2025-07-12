#!/usr/bin/python3
"""
Decorator that logs database queries executed by any function
"""

import sqlite3
import functools


def log_queries(func):
    """
    Decorator to log SQL queries before executing them.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The decorated function that logs queries
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from arguments
        query = None
        if 'query' in kwargs:
            query = kwargs['query']
        elif args:
            # Look for query parameter in args
            for arg in args:
                if isinstance(arg, str) and ('SELECT' in arg.upper() or 'UPDATE' in arg.upper() or 'INSERT' in arg.upper() or 'DELETE' in arg.upper()):
                    query = arg
                    break
        
        # Log the query if found
        if query:
            print(f"Executing query: {query}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Fetched {len(users)} users")