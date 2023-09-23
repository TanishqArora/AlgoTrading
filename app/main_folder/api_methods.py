import pandas as pd
import requests
import json
import configparser
import generate_symbols
import sqlite3
import database_setup
from datetime import datetime, timedelta


def get_access_token():
    """
    Retrieve an access token from a JSON file.

    This function reads a JSON file located at '../csv/authentication.json', which is expected to contain an 'access_token'
    field. It extracts and returns the 'access_token' from the JSON content.

    Returns:
        str: The access token extracted from the JSON file.

    Raises:
        FileNotFoundError: If the JSON file at '../csv/authentication.json' does not exist.
        KeyError: If the 'access_token' field is not found in the JSON content.

    Example:
        # Assuming '../csv/authentication.json' contains: {"access_token": "example_token"}
        token = get_access_token()
        print(token)  # Output: "example_token"
    """
    with open('../csv/authentication.json', 'r') as openfile:
        json_response = json.load(openfile)

    ACCESS_TOKEN = json_response['access_token']
    return ACCESS_TOKEN

ACCESS_TOKEN = get_access_token()

def get_config():
    """
    Retrieve a configuration object from a configuration file.

    This function reads a configuration file named 'config.cfg' using the `configparser` library
    and returns a `ConfigParser` object containing the configuration settings.

    Returns:
        configparser.ConfigParser: A ConfigParser object containing the configuration settings.

    Raises:
        FileNotFoundError: If the 'config.cfg' file does not exist or cannot be found.
        configparser.Error: If there is an issue parsing the configuration file.

    Example:
        # Assuming 'config.cfg' contains configuration settings
        config = get_config()
        value = config.get('section_name', 'setting_name')
        print(value)  # Retrieve and print a configuration setting
    """
    # Reading from Config file
    config = configparser.ConfigParser()
    config.read('config.cfg')
    return config


def convert_to_nearest(num):
    nearest_0 = round(num * 20) / 20  # Round to nearest 0.05
    nearest_5 = round(num * 20 + 5) / 20  # Round to nearest 0.05 and add 0.05
    
    if abs(nearest_0 - num) < abs(nearest_5 - num):
        return nearest_0
    else:
        return nearest_5

def get_current_funds():
    """
    Retrieve the current available funds from an Upstox API.

    This function sends a GET request to the Upstox API endpoint 'https://api-v2.upstox.com/user/get-funds-and-margin'
    to fetch the available margin for the 'SEC' segment. It uses the provided ACCESS_TOKEN for authorization.

    Returns:
        int: The current available funds as an integer.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
        KeyError: If the expected data structure in the JSON response is not found.

    Example:
        # Assuming ACCESS_TOKEN is obtained from a valid source
        funds = get_current_funds()
        print(funds)  # Output: Current available funds as an integer
    """
    URL = 'https://api-v2.upstox.com/user/get-funds-and-margin'

    headers = {
        'accept': 'application/json',
        'Api-Version': '2.0',
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }

    params = {
        'segment': 'SEC'
    }

    response = requests.get(URL, headers=headers, params=params)
    json_response = response.json()
    current_funds = int(json_response['data']['equity']['available_margin'])
    return current_funds


def get_ltp_data(instrument_key):
    """
    Retrieve the Last Traded Price (LTP) data for a given instrument key from Upstox API.

    This function sends a GET request to the Upstox API endpoint 'https://api-v2.upstox.com/market-quote/ltp'
    to fetch the LTP data for the specified instrument. It uses the provided ACCESS_TOKEN for authorization.

    Args:
        instrument_key (str): The instrument key for the desired instrument.

    Returns:
        float: The Last Traded Price (LTP) as a floating-point number.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
        KeyError: If the expected data structure in the JSON response is not found.

    Example:
        # Assuming ACCESS_TOKEN is obtained from a valid source
        ltp = get_ltp_data('NSE_EQ|RELIANCE')
        print(ltp)  # Output: Last Traded Price as a floating-point number
    """
    url = 'https://api-v2.upstox.com/market-quote/ltp'
    params = {
        'symbol': instrument_key
    }
    headers = {
        'accept': 'application/json',
        'Api-Version': '2.0',
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        trading_symbol = generate_symbols.get_trading_symbol_from_instrument_key(instrument_key)
        key_ = str(instrument_key.split('|')[0]) + ':' + str(trading_symbol) if str(instrument_key.split('|')[0]) != 'NSE_INDEX' else str(instrument_key.replace('|', ':'))
        return data['data'][key_]['last_price']
    else:
        print('Request failed with status code:', response.status_code)
        return response.status_code


def start_end_date():
    """
    Generate start and end dates for a date range.

    This function calculates the start and end dates for a date range, typically used for fetching data
    within the last 30 days up to the day before the current date.

    Returns:
        tuple: A tuple containing two strings representing the start and end dates in 'YYYY-MM-DD' format.

    Example:
        start, end = start_end_date()
        print(start, end)  # Output: Start and end dates in 'YYYY-MM-DD' format
    """
    today = datetime.now()
    start_date = today - timedelta(days=30)
    end_date = today - timedelta(days=1)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    return start_date_str, end_date_str


start_date_str,end_date_str = start_end_date()


def get_ohlc(symbol, interval='1minute', start_date=None, end_date=None):
    """
    Retrieve OHLC (Open, High, Low, Close) data for a specified symbol and time interval from Upstox API.

    This function sends a GET request to the Upstox API to fetch OHLC data for the specified symbol, time interval,
    and date range. By default, it fetches data for the last 30 days, but you can provide custom start and end dates.

    Args:
        symbol (str): The symbol for which you want to retrieve OHLC data (e.g., 'NSE_EQ|RELIANCE').
        interval (str): The time interval for OHLC data (default is '1minute').
        start_date (str, optional): The start date in 'YYYY-MM-DD' format (default is the start date generated by 'start_end_date' function).
        end_date (str, optional): The end date in 'YYYY-MM-DD' format (default is the end date generated by 'start_end_date' function).

    Returns:
        pandas.DataFrame or None: A DataFrame containing OHLC data if the request is successful, or None if the request fails.

    Example:
        # Assuming 'start_end_date' function has been defined earlier to get start and end dates
        ohlc_data = get_ohlc('NSE_EQ|RELIANCE', interval='5minute', start_date='2023-01-01', end_date='2023-01-31')
        print(ohlc_data)  # Output: DataFrame with OHLC data for the specified symbol and date range
    """
    if start_date is None or end_date is None:
        start_date, end_date = start_end_date()

    url = f'https://api-v2.upstox.com/historical-candle/{symbol}/{interval}/{end_date}/{start_date}'
    
    headers = {
        'accept': 'application/json',
        'Api-Version': '2.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        data = pd.DataFrame(data['data']['candles'], columns=['Time', 'Open', 'High', 'Low', 'Close', 'unk1', 'unk2'])
        return data
    else:
        print(response.json())
        print(f"Request failed with status code: {response.status_code}")
        return None


def get_order_status(order_id):
    """
    Retrieve the status of a specific order from Upstox API.

    This function sends a GET request to the Upstox API endpoint 'https://api-v2.upstox.com/order/history'
    to fetch the status of the specified order using its order ID. It uses the provided ACCESS_TOKEN for authorization.

    Args:
        order_id (str): The order ID for the order whose status you want to retrieve.

    Returns:
        str or dict or None: The order status as a string ('Completed' for 'complete' status, or the full response data as a dictionary) if the request is successful, or None if the request fails.

    Example:
        # Assuming ACCESS_TOKEN is obtained from a valid source
        order_status = get_order_status('1234567890')
        print(order_status)  # Output: 'Completed' or the full response data
    """
    url = 'https://api-v2.upstox.com/order/history'

    params = {
        'order_id': order_id
    }
    headers = {
        'accept': 'application/json',
        'Api-Version': '2.0',
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        temp_df = pd.DataFrame(data['data'])
        status = temp_df[temp_df['order_id'] == order_id].tail(1)['status'].values[0]
        if status == 'complete':
            return 'Completed'
        else:
            return data
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.json())
        return None


def get_order_avg_price(order_id):
    """
    Retrieve the average price of a specific order from Upstox API.

    This function sends a GET request to the Upstox API endpoint 'https://api-v2.upstox.com/order/history'
    to fetch the average price of the specified order using its order ID. It uses the provided ACCESS_TOKEN for authorization.

    Args:
        order_id (str): The order ID for the order whose average price you want to retrieve.

    Returns:
        float or None: The average price as a floating-point number if the request is successful, or None if the request fails.

    Example:
        # Assuming ACCESS_TOKEN is obtained from a valid source
        avg_price = get_order_avg_price('1234567890')
        print(avg_price)  # Output: Average price as a floating-point number
    """
    url = f'https://api-v2.upstox.com/order/history?order_id={order_id}'

    headers = {
        'accept': 'application/json',
        'Api-Version': '2.0',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and data['data']:
            temp_df = pd.DataFrame(data['data'])
            order_data = temp_df[temp_df['order_id'] == order_id]
            if not order_data.empty:
                average_price = order_data['average_price'].iloc[-1]
                if average_price > 0:
                    return average_price
                else:
                    print(f'Order Status Returning Data: {data}')
            else:
                print(f'Order {order_id} not found in data')
        else:
            print('No data found in the response')
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.json())

    return None


def cancel_order(order_id):
    """
    Cancel a specific order using its order ID via the Upstox API.

    This function sends a DELETE request to the Upstox API endpoint 'https://api-v2.upstox.com/order/cancel'
    to cancel the order with the specified order ID. It uses the provided ACCESS_TOKEN for authorization.

    Args:
        order_id (str): The order ID of the order you want to cancel.

    Example:
        # Assuming ACCESS_TOKEN is obtained from a valid source
        cancel_order('1234567890')
    """
    url = 'https://api-v2.upstox.com/order/cancel'
    headers = {
        'accept': 'application/json',
        'Api-Version': '2.0',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    params = {
        'order_id': order_id
    }

    response = requests.delete(url, headers=headers, params=params)

    if response.status_code == 200:
        print("Order canceled successfully.")
    else:
        print("Failed to cancel the order. Status code:", response.status_code)
        print("Response:", response.text)


def get_ltp_websocket(instrument_key):
    """
    Retrieve the Last Traded Price (LTP) for a specific instrument from a SQLite database.

    This function connects to a SQLite database located at '../database/test_database.db' and retrieves the LTP
    for the specified instrument_key. It compares the stored timestamp in the database with the current time
    to check if the LTP is up-to-date.

    Args:
        instrument_key (str): The instrument key for the desired instrument (e.g., 'NSE_EQ|RELIANCE').

    Returns:
        float or None: The Last Traded Price (LTP) as a floating-point number if it's up-to-date, or None if it's not updated.

    Example:
        # Assuming 'get_current_time_asia_kolkata' is a function defined elsewhere to get current time
        ltp = get_ltp_websocket('NSE_EQ|RELIANCE')
        print(ltp)  # Output: LTP as a floating-point number or None
    """
    # Connect to the SQLite database
    with sqlite3.connect('../database/test_database.db') as sql_conn:
        # Use parameterized query to prevent SQL injection
        query = """
            SELECT year, month, day, hour, minute, second, price
            FROM {}
            ORDER BY year DESC, month DESC, day DESC, hour DESC, minute DESC, second DESC
            LIMIT 1
        """.format(instrument_key.replace('|', '').replace(' ', ''))
        
        df = pd.read_sql_query(query, sql_conn)

    year, month, day, hour, minute, second, millisecond = database_setup.get_current_time_asia_kolkata()  # Assuming 'get_current_time_asia_kolkata' is a function defined elsewhere to get current time
    current_time = (year, month, day, hour, minute, second)

    if (not df.empty and
        (df.iloc[0]['year'], df.iloc[0]['month'], df.iloc[0]['day'],
        df.iloc[0]['hour'], df.iloc[0]['minute'], df.iloc[0]['second']) == current_time):
        return df.iloc[0]['price']
    else:
        # LTP is not updated
        return None



def get_order_status_websocket(order_id):
    """
    Retrieve the status of a specific order from a SQLite database.

    This function connects to a SQLite database located at '../database/test_database.db' and retrieves the status
    of the specified order using its order ID. It checks the status and average traded price, if available, from
    the most recent record in the database.

    Args:
        order_id (str): The order ID for the order whose status you want to retrieve.

    Returns:
        str or None: The order status as a string ('Completed' for 'complete' status, or the actual status from the database) if a matching record is found, or None if no matching record is found.

    Example:
        order_status = get_order_status_websocket('1234567890')
        print(order_status)  # Output: 'Completed' or the actual status from the database or None
    """
    # Connect to the SQLite database
    with sqlite3.connect('../database/test_database.db') as sql_conn:
        # Use parameterized query to prevent SQL injection
        query = """
            SELECT status, average_traded_price
            FROM portfolio
            WHERE order_id = {}
            ORDER BY time DESC
            LIMIT 1
        """.format(order_id)
        
        df = pd.read_sql_query(query, sql_conn)

    if df.empty:
        return None
    elif df['status'].values[0] == 'complete':
        return 'Completed'
    else:
        return df['status']

    

# def get_ltp(instrument_key):
#     ltp = get_ltp_websocket(instrument_key)
#     if ltp is not None:
#         return ltp
#     else:
#         print('Check Websocket, retriving LTP with api')
#         return get_ltp_data(instrument_key)
    

# def get_status(instrument_key):
#     status = get_order_status_websocket(instrument_key)
#     if status is not None:
#         return status
#     else:
#         print('Check Websocket, retriving LTP with api')
#         return get_ltp_data(instrument_key)