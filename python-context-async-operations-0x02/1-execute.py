import sqlite3

class ExecuteQuery:
    """A reusable class-based context manager for executing database queries."""
    
    def __init__(self, db_name, query, params=None):
        """Initialize the query execution context manager.
        
        Args:
            db_name (str): The name of the database file
            query (str): The SQL query to execute
            params (tuple, optional): Parameters for the query
        """
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """Enter the context manager, establish connection, and execute query.
        
        Returns:
            list: The results of the query execution
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Database connection to '{self.db_name}' established.")
            
            # Execute the query with parameters
            self.cursor.execute(self.query, self.params)
            self.results = self.cursor.fetchall()
            
            print(f"Query executed successfully: {self.query}")
            if self.params:
                print(f"Parameters: {self.params}")
            
            return self.results
            
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and close database connection.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()
            print(f"Database connection to '{self.db_name}' closed.")
        
        # Return False to propagate any exceptions
        return False


def setup_database(db_name):
    """Set up a sample database with users table and data."""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Insert sample data with various ages
        sample_users = [
            ('Alice Johnson', 28, 'alice@example.com'),
            ('Bob Smith', 35, 'bob@example.com'),
            ('Charlie Brown', 42, 'charlie@example.com'),
            ('Diana Prince', 31, 'diana@example.com'),
            ('Eve Davis', 29, 'eve@example.com'),
            ('Frank Wilson', 45, 'frank@example.com'),
            ('Grace Lee', 38, 'grace@example.com'),
            ('Henry Taylor', 52, 'henry@example.com'),
            ('Ivy Chen', 26, 'ivy@example.com'),
            ('Jack Miller', 33, 'jack@example.com')
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO users (name, age, email) VALUES (?, ?, ?)',
            sample_users
        )
        
        conn.commit()
        print("Sample database setup completed.")


def main():
    """Main function to demonstrate the ExecuteQuery context manager."""
    db_name = "example.db"
    
    # Set up the database
    setup_database(db_name)
    
    # Use the ExecuteQuery context manager to query users older than 25
    query = "SELECT * FROM users WHERE age > ?"
    age_threshold = 25
    
    print("\n" + "=" * 60)
    print("EXECUTING QUERY WITH CONTEXT MANAGER")
    print("=" * 60)
    
    with ExecuteQuery(db_name, query, (age_threshold,)) as results:
        print(f"\nFound {len(results)} users older than {age_threshold}:")
        print("-" * 60)
        print(f"{'ID':<5} {'Name':<15} {'Age':<5} {'Email':<25}")
        print("-" * 60)
        
        for row in results:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<5} {row[3]:<25}")
    
    # Demonstrate with a different query
    print("\n" + "=" * 60)
    print("SECOND QUERY DEMONSTRATION")
    print("=" * 60)
    
    query2 = "SELECT name, age FROM users WHERE age BETWEEN ? AND ?"
    min_age, max_age = 30, 45
    
    with ExecuteQuery(db_name, query2, (min_age, max_age)) as results:
        print(f"\nUsers between ages {min_age} and {max_age}:")
        print("-" * 30)
        print(f"{'Name':<15} {'Age':<5}")
        print("-" * 30)
        
        for row in results:
            print(f"{row[0]:<15} {row[1]:<5}")


if __name__ == "__main__":
    main()