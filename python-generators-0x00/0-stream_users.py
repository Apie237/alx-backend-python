#!/usr/bin/python3
"""
Generator that streams rows from an SQL database one by one
"""

import seed


def stream_users():
    """
    Generator function that yields rows one by one from the user_data table.
    Uses yield to create a generator that fetches rows from the database.
    """
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        # Yield each row one by one
        for row in cursor:
            yield row
        
        cursor.close()
        connection.close()