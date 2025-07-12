#!/usr/bin/python3
"""
Batch processing for large data using generators
"""

import seed


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows in batches from the user_data table.
    
    Args:
        batch_size (int): Number of rows to fetch in each batch
    
    Yields:
        list: A batch of user records
    """
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
        
        cursor.close()
        connection.close()


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.
    
    Args:
        batch_size (int): Number of rows to process in each batch
    """
    # Process users in batches
    for batch in stream_users_in_batches(batch_size):
        # Filter users over age 25 in current batch
        for user in batch:
            if user['age'] > 25:
                print(user)