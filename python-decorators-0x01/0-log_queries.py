import sqlite3
import functools

#### decorator to log SQL queries

def log_queries(func):
    """Decorator that logs SQL queries before executing them"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from the function arguments
        # Assuming the query is passed as a keyword argument or as the first positional argument
        query = None
        
        # Check if 'query' is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if there are positional arguments and assume the first one might be the query
        elif args:
            # Look for query in args - it could be any argument that looks like SQL
            for arg in args:
                if isinstance(arg, str) and ('SELECT' in arg.upper() or 'INSERT' in arg.upper() or 
                                           'UPDATE' in arg.upper() or 'DELETE' in arg.upper()):
                    query = arg
                    break
        
        # Log the query if found
        if query:
            print(f"Executing SQL Query: {query}")
        
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

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")