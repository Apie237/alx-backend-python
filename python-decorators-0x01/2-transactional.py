import sqlite3 
import functools

def with_db_connection(func):
    """Decorator that automatically handles opening and closing database connections"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('example.db')
        try:
            # Call the original function with the connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection
            conn.close()
    return wrapper

def transactional(func):
    """Decorator that manages database transactions by automatically committing or rolling back changes"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Start transaction (implicit with sqlite3)
            result = func(conn, *args, **kwargs)
            # Commit if no exception occurred
            conn.commit()
            return result
        except Exception as e:
            # Rollback if an exception occurred
            conn.rollback()
            raise e
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

#### Update user's email with automatic transaction handling 
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')