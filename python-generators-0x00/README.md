# Python Generators - Database Operations

This project demonstrates the use of Python generators for efficient database operations, including streaming data, batch processing, lazy pagination, and memory-efficient aggregations.

## Files Overview

### 1. `seed.py`
Database setup script that:
- Connects to MySQL database server
- Creates the `ALX_prodev` database
- Creates the `user_data` table with required fields
- Populates the table with sample data from CSV

**Functions:**
- `connect_db()`: Connects to MySQL server
- `create_database(connection)`: Creates ALX_prodev database
- `connect_to_prodev()`: Connects to ALX_prodev database
- `create_table(connection)`: Creates user_data table
- `insert_data(connection, data)`: Inserts CSV data into table

### 2. `0-stream_users.py`
Implements a generator that streams database rows one by one.

**Functions:**
- `stream_users()`: Generator that yields user records individually

### 3. `1-batch_processing.py`
Implements batch processing for large datasets.

**Functions:**
- `stream_users_in_batches(batch_size)`: Generator that fetches rows in batches
- `batch_processing(batch_size)`: Processes batches to filter users over age 25

### 4. `2-lazy_paginate.py`
Implements lazy pagination for database queries.

**Functions:**
- `paginate_users(page_size, offset)`: Fetches paginated results
- `lazy_paginate(page_size)`: Generator for lazy pagination

### 5. `4-stream_ages.py`
Implements memory-efficient aggregation using generators.

**Functions:**
- `stream_user_ages()`: Generator that yields user ages one by one
- `calculate_average_age()`: Calculates average age without loading all data

## Database Schema

The `user_data` table has the following structure:
- `user_id` (VARCHAR(36), Primary Key, Indexed)
- `name` (VARCHAR(255), NOT NULL)
- `email` (VARCHAR(255), NOT NULL)
- `age` (DECIMAL(3,0), NOT NULL)

## Key Features

1. **Memory Efficiency**: Uses generators to process large datasets without loading everything into memory
2. **Lazy Evaluation**: Data is fetched only when needed
3. **Batch Processing**: Handles large datasets in manageable chunks
4. **Database Streaming**: Processes database rows one by one
5. **Pagination**: Implements lazy pagination for better performance

## Usage Examples

```python
# Stream users one by one
for user in stream_users():
    print(user)

# Process users in batches
batch_processing(50)

# Lazy pagination
for page in lazy_paginate(100):
    for user in page:
        print(user)

# Calculate average age efficiently
average_age = calculate_average_age()
print(f"Average age: {average_age}")
```

## Requirements

- Python 3.x
- MySQL database server
- `mysql-connector-python` package
- CSV file with user data

## Setup

1. Install MySQL connector: `pip install mysql-connector-python`
2. Set up MySQL database with appropriate credentials
3. Run `seed.py` to create database and tables
4. Ensure CSV file with user data is available
5. Run the individual scripts as needed