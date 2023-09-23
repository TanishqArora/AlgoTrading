import sqlite3
import time
import datetime
import pytz

def get_current_time(websocket_timestamp):
    """
    Convert a WebSocket timestamp to a tuple of date and time components in the Indian time zone.

    This function takes a WebSocket timestamp, converts it to a datetime object, and then converts it to the Indian
    time zone ('Asia/Kolkata'). It extracts and returns the year, month, day, hour, minute, second, and millisecond components.

    Args:
        websocket_timestamp (int): The WebSocket timestamp to be converted.

    Returns:
        tuple: A tuple containing year, month, day, hour, minute, second, and millisecond components.

    Example:
        timestamp = 1632403200000  # Example WebSocket timestamp (milliseconds since epoch)
        time_components = get_current_time(timestamp)
        print(time_components)  # Output: Tuple containing date and time components
    """
    # Convert the timestamp to a datetime object
    timestamp = websocket_timestamp / 1000  # Convert to seconds
    timestamp_datetime = datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)

    # Convert to Indian time zone
    indian_timezone = pytz.timezone('Asia/Kolkata')
    indian_time = timestamp_datetime.astimezone(indian_timezone)

    # Extract individual components
    year = indian_time.year
    month = indian_time.month
    day = indian_time.day
    hour = indian_time.hour
    minute = indian_time.minute
    second = indian_time.second
    millisecond = indian_time.microsecond // 1000

    return year, month, day, hour, minute, second, millisecond

    

def insert_into_table(table_name, data_dict):
    """
    Insert data into a SQLite table.

    This function connects to a SQLite database located at '../database/test_database.db' and inserts data into
    the specified table. It creates the table if it doesn't exist.

    Args:
        table_name (str): The name of the table where data will be inserted.
        data_dict (dict): A dictionary containing the data to be inserted. The keys should match the column names in the table.

    Example:
        data = {
            'symbol': 'AAPL',
            'year': 2023,
            'month': 9,
            'day': 23,
            'hour': 14,
            'minute': 30,
            'second': 45,
            'millisecond': 500,
            'price': 150.25
        }
        insert_into_table('my_table', data)
    """
    start_time = time.perf_counter()
    # Connect to the SQLite database
    conn = sqlite3.connect('../database/test_database.db')
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            symbol TEXT,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            hour INTEGER,
            minute INTEGER,
            second INTEGER,
            millisecond INTEGER,
            price REAL
        )
    ''')

    # Insert data into the table using parameterized query
    insert_query = f'''
        INSERT INTO {table_name} (symbol, year, month, day, hour, minute, second, millisecond, price)
        VALUES (:symbol, :year, :month, :day, :hour, :minute, :second, :millisecond, :price)
    '''

    cursor.execute(insert_query, data_dict)

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f'Data inserted into {table_name}: {time.perf_counter() - start_time}')

def time_now():
    """
    Get the current time in the Indian time zone.

    This function retrieves the current time as a datetime object in the Indian time zone ('Asia/Kolkata').

    Returns:
        datetime.datetime: The current time in the Indian time zone.

    Example:
        current_time = time_now()
        print(current_time)  # Output: Current time as a datetime object in the Indian time zone
    """
    timestamp_datetime = datetime.datetime.fromtimestamp(time.time(), tz=pytz.utc)
    indian_timezone = pytz.timezone('Asia/Kolkata')
    indian_time = timestamp_datetime.astimezone(indian_timezone)
    return indian_time


def get_current_time_asia_kolkata():
    """
    Get the current time in the Asia/Kolkata time zone and extract its components.

    This function retrieves the current time in the Asia/Kolkata time zone ('Asia/Kolkata') and extracts
    the year, month, day, hour, minute, second, and millisecond components.

    Returns:
        tuple: A tuple containing year, month, day, hour, minute, second, and millisecond components.

    Example:
        time_components = get_current_time_asia_kolkata()
        print(time_components)  # Output: Tuple containing date and time components
    """
    # Get the current time in UTC
    current_time_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    # Convert to the Asia/Kolkata time zone
    indian_timezone = pytz.timezone('Asia/Kolkata')
    current_time_kolkata = current_time_utc.astimezone(indian_timezone)

    # Extract individual components
    year = current_time_kolkata.year
    month = current_time_kolkata.month
    day = current_time_kolkata.day
    hour = current_time_kolkata.hour
    minute = current_time_kolkata.minute
    second = current_time_kolkata.second
    millisecond = current_time_kolkata.microsecond // 1000

    return year, month, day, hour, minute, second, millisecond


def market_opened():
    """
    Check if the stock market is currently open in the Asia/Kolkata time zone.

    This function checks whether the stock market is currently open based on the current time in the Asia/Kolkata
    time zone. The market is considered open from 9:15 AM to 3:30 PM.

    Returns:
        bool: True if the market is open, False if the market is closed.

    Example:
        is_market_open = market_opened()
        print(is_market_open)  # Output: True if the market is open, False if the market is closed
    """
    current_time = datetime.datetime.fromtimestamp(time.time(), tz=pytz.timezone('Asia/Kolkata'))
    market_opening_time = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    market_closing_time = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
    
    if (current_time >= market_opening_time) and (current_time <= market_closing_time):
        return True
    else:
        return False

    
def insert_into_portfolio(table_name, data_dict):
    """
    Insert data into a portfolio SQLite table.

    This function connects to a SQLite database located at '../database/test_database.db' and inserts data into
    the specified portfolio table. It creates the table if it doesn't exist.

    Args:
        table_name (str): The name of the portfolio table where data will be inserted.
        data_dict (dict): A dictionary containing the data to be inserted. The keys should match the column names in the portfolio table.

    Example:
        data = {
            'time': '2023-09-23 14:30:45.500000',  # Example timestamp
            'order_id': '1234567890',
            'status': 'complete',
            'average_traded_price': 150.25
        }
        insert_into_portfolio('my_portfolio', data)
    """
    start_time = time.perf_counter()
    # Connect to the SQLite database
    conn = sqlite3.connect('../database/test_database.db')
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            time TIMESTAMP,
            order_id TEXT,
            status TEXT,
            average_traded_price REAL
        )
    ''')

    # Insert data into the portfolio table using parameterized query
    insert_query = f'''
        INSERT INTO {table_name} (time, order_id, status, average_traded_price)
        VALUES (:time, :order_id, :status, :average_traded_price)
    '''

    cursor.execute(insert_query, data_dict)

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f'Data inserted into {table_name}: {time.perf_counter() - start_time}')
