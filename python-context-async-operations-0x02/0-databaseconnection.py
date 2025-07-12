import sqlite3

class DatabaseConnection:
    """A class-based context manager for database connections."""
    
    def __init__(self, db_name):
        """Initialize the database connection manager.
        
        Args:
            db_name (str): The name of the database file
        """
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """Enter the context manager and establish database connection.
        
        Returns:
            sqlite3.Cursor: The database cursor for executing queries
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Database connection to '{self.db_name}' established.")
            return self.cursor
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
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


def main():
    """Main function to demonstrate the DatabaseConnection context manager."""
    # Create a sample database and table for demonstration
    db_name = "example.db"
    
    # First, let's create the database and insert some sample data
    with DatabaseConnection(db_name) as cursor:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Insert sample data
        sample_users = [
            ('Alice Johnson', 28, 'alice@example.com'),
            ('Bob Smith', 35, 'bob@example.com'),
            ('Charlie Brown', 42, 'charlie@example.com'),
            ('Diana Prince', 31, 'diana@example.com'),
            ('Eve Davis', 29, 'eve@example.com')
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO users (name, age, email) VALUES (?, ?, ?)',
            sample_users
        )
        print("Sample data inserted successfully.")
    
    # Now use the context manager to query the database
    with DatabaseConnection(db_name) as cursor:
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        print("\nQuery Results:")
        print("=" * 50)
        print(f"{'ID':<5} {'Name':<15} {'Age':<5} {'Email':<25}")
        print("-" * 50)
        
        for row in results:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<5} {row[3]:<25}")


if __name__ == "__main__":
    main()