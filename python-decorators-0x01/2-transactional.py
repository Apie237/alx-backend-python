#!/usr/bin/python3
"""
Decorator that manages database transactions by automatically committing or rolling back changes
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


def transactional(func):
    """
    Decorator that ensures a function running a database operation is wrapped
    inside a transaction. If the function raises an error, rollback; otherwise
    commit the transaction.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The decorated function with transaction management
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Begin transaction (SQLite begins automatically)
            result = func(conn, *args, **kwargs)
            # Commit if no exception occurred
            conn.commit()
            return result
        except Exception as e:
            # Rollback on any exception
            conn.rollback()
            raise e
    
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


if __name__ == "__main__":
    # Update user's email with automatic transaction handling
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    print("User email updated successfully")