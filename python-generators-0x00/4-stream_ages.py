#!/usr/bin/python3
"""
Memory-efficient aggregation using generators to compute average age
"""

import seed


def stream_user_ages():
    """
    Generator that yields user ages one by one from the database.
    
    Yields:
        int: User age
    """
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        # Yield each age one by one
        for row in cursor:
            yield row[0]
        
        cursor.close()
        connection.close()


def calculate_average_age():
    """
    Calculate the average age of all users using the generator.
    This method is memory-efficient as it doesn't load all data at once.
    
    Returns:
        float: Average age of users
    """
    total_age = 0
    count = 0
    
    # Use generator to process ages one by one
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count > 0:
        return total_age / count
    return 0


if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age}")