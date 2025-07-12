#!/usr/bin/python3
"""
Decorator that retries database operations if they fail due to transient errors
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


def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries the function a certain number of times if it raises an exception.
    
    Args:
        retries (int): Number of retry attempts (default: 3)
        delay (int): Delay between retries in seconds (default: 2)
        
    Returns:
        The decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):  # +1 to include the first attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retries:  # Don't delay after the last attempt
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print(f"All {retries + 1} attempts failed.")
            
            # If all retries failed, raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    # Attempt to fetch users with automatic retry on failure
    try:
        users = fetch_users_with_retry()
        print(f"Successfully fetched {len(users)} users")
    except Exception as e:
        print(f"Failed to fetch users after retries: {e}")