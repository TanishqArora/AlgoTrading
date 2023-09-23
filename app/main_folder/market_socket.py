import asyncio
import json
import websockets
import database_setup
from google.protobuf.json_format import ParseDict
import api_methods
from MarketDataFeed_pb2 import FeedResponse  # Import the generated protobuf classes
import multiprocessing
import time
import argparse
import sys

def subscribe_to_stock(subscribed_stock):

    async def main():

        print('Market Opened starting sync operation')
        websocket_url = api_methods.get_config().get('INDEX', 'websocket_url')
        ACCESS_TOKEN = api_methods.get_access_token()
        timeout_seconds = 60

        async with websockets.connect(websocket_url, ping_interval=timeout_seconds, extra_headers={
            "Api-Version": "2.0",
            "Authorization": "Bearer " + ACCESS_TOKEN,
        }) as ws:
            print("connected")

            await asyncio.sleep(1)  # Sleep for 1 second

            data = {
                "guid": "someguid",
                "method": "sub",
                "data": {
                    "mode": "full",
                    "instrumentKeys": [subscribed_stock]
                }
            }
            await ws.send(json.dumps(data).encode())

            async for message in ws:
                feed_response = FeedResponse()
                feed_response.ParseFromString(message)
                if subscribed_stock.startswith('NSE_INDEX'):
                    current_price = feed_response.feeds[subscribed_stock].ff.indexFF.ltpc.ltp
                    current_year, current_month, current_day, current_hour, current_minute, current_second,current_millisecond = database_setup.get_current_time_asia_kolkata()

                elif subscribed_stock.startswith('NSE_FO'):
                    current_price = feed_response.feeds[subscribed_stock].ff.marketFF.ltpc.ltp
                    current_year, current_month, current_day, current_hour, current_minute, current_second,current_millisecond = database_setup.get_current_time_asia_kolkata()

                data_dict = {
                    'symbol': subscribed_stock,
                    'year': current_year,
                    'month': current_month,
                    'day': current_day,
                    'hour': current_hour,
                    'minute': current_minute,
                    'second': current_second,
                    'millisecond': current_millisecond,
                    'price': current_price
                }
                # print(data_dict)
                database_setup.insert_into_table(subscribed_stock.replace('|','').replace(' ', ''), data_dict)

            print("disconnected")

    if __name__ == "__main__":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

def start_sync(stock):
    print(f'Websocket Sync for {stock} waiting for market to open...')

    while True:
        while not database_setup.market_opened():
            time.sleep(1)
        
        print(f'Websocket Sync for {stock} started')
        p = multiprocessing.Process(target=subscribe_to_stock, args=(stock,))
        p.start()

        while database_setup.market_opened():
            time.sleep(1)

        print(f'Websocket Sync for {stock} stopping...')
        p.terminate()
        p.join()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="WebSocket synchronization for stock symbols")
    parser.add_argument("symbols", nargs='+', help="List of stock symbols to sync (up to 3)")

    args = parser.parse_args()

    if len(args.symbols) > 3:
        print("Error: You can specify up to 3 stock symbols.")
        parser.print_help()
        sys.exit(1)

    SUBSCRIBED_STOCKS = args.symbols
    # How to use
    # SUBSCRIBED_STOCKS = ['NSE_INDEX|Nifty 50', 'NSE_INDEX|Nifty Bank', 'NSE_INDEX|Nifty Fin Service']
    # python market_socket.py 'NSE_INDEX|Nifty 50' 'NSE_INDEX|Nifty Bank' 'NSE_INDEX|Nifty Fin Service'
    # SUBSCRIBED_STOCKS = ['NSE_FO|54643', 'NSE_FO|54644']

    processes = []
    for stock in SUBSCRIBED_STOCKS:
        process = multiprocessing.Process(target=start_sync, args=(stock,))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()