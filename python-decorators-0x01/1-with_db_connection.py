#!/usr/bin/python3
"""
Decorator that automatically handles opening and closing database connections
"""

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


@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


if __name__ == "__main__":
    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    print(user)