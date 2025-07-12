import asyncio
import aiosqlite
import sqlite3

async def async_fetch_users():
    """Asynchronously fetch all users from the database.
    
    Returns:
        list: List of all users from the database
    """
    async with aiosqlite.connect("example.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            print(f"async_fetch_users: Retrieved {len(users)} users")
            return users

async def async_fetch_older_users():
    """Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: List of users older than 40
    """
    async with aiosqlite.connect("example.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            older_users = await cursor.fetchall()
            print(f"async_fetch_older_users: Retrieved {len(older_users)} users older than 40")
            return older_users

async def fetch_concurrently():
    """Execute both fetch functions concurrently using asyncio.gather.
    
    Returns:
        tuple: Results from both async functions
    """
    print("Starting concurrent database queries...")
    print("-" * 50)
    
    # Use asyncio.gather to run both queries concurrently
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    all_users, older_users = results
    
    print("\n" + "=" * 60)
    print("CONCURRENT QUERY RESULTS")
    print("=" * 60)
    
    # Display all users
    print(f"\nAll Users ({len(all_users)} total):")
    print("-" * 60)
    print(f"{'ID':<5} {'Name':<15} {'Age':<5} {'Email':<25}")
    print("-" * 60)
    for user in all_users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<5} {user[3]:<25}")
    
    # Display older users
    print(f"\nUsers Older Than 40 ({len(older_users)} total):")
    print("-" * 60)
    print(f"{'ID':<5} {'Name':<15} {'Age':<5} {'Email':<25}")
    print("-" * 60)
    for user in older_users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<5} {user[3]:<25}")
    
    return all_users, older_users

def setup_database():
    """Set up a sample database with users table and data."""
    with sqlite3.connect("example.db") as conn:
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
        
        # Insert sample data with various ages (including users over 40)
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
            ('Jack Miller', 33, 'jack@example.com'),
            ('Kate Rodriguez', 48, 'kate@example.com'),
            ('Liam Foster', 41, 'liam@example.com'),
            ('Maya Patel', 39, 'maya@example.com'),
            ('Noah Kim', 44, 'noah@example.com'),
            ('Olivia Zhang', 37, 'olivia@example.com')
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO users (name, age, email) VALUES (?, ?, ?)',
            sample_users
        )
        
        conn.commit()
        print("Sample database setup completed.")

def main():
    """Main function to demonstrate concurrent async database queries."""
    print("Setting up database...")
    setup_database()
    
    print("\n" + "=" * 60)
    print("CONCURRENT ASYNC DATABASE OPERATIONS")
    print("=" * 60)
    
    # Run the concurrent fetch using asyncio.run
    asyncio.run(fetch_concurrently())
    
    print("\n" + "=" * 60)
    print("CONCURRENT OPERATIONS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()