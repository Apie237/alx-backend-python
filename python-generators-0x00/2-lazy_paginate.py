#!/usr/bin/python3
"""
Lazy loading paginated data using generators
"""

import seed


def paginate_users(page_size, offset):
    """
    Fetch users with pagination from the database.
    
    Args:
        page_size (int): Number of users per page
        offset (int): Starting position for the page
    
    Returns:
        list: List of user records for the current page
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """
    Generator that lazily loads pages of users.
    Only fetches the next page when needed.
    
    Args:
        page_size (int): Number of users per page
    
    Yields:
        list: A page of user records
    """
    offset = 0
    
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size


# Alias for the main function to match the test requirements
lazy_pagination = lazy_paginate