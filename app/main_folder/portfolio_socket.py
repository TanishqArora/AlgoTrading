import asyncio
import websockets
import api_methods
import json
import database_setup

websocket_url = api_methods.get_config().get('INDEX', 'portfoliosocket_url')
ACCESS_TOKEN = api_methods.get_access_token()
timeout_seconds = 60

async def on_message(data):
    current_time = database_setup.time_now()
    dict = json.loads(data) 
    data_dict = {
                    'time': current_time,
                    'order_id': dict['order_id'],
                    'status': dict['status'],
                    'average_traded_price': dict['average_price']
                }
    database_setup.insert_into_portfolio('portfolio', data_dict)
    print(dict)

async def connect_websocket():
    
    headers = {
        "Api-Version": "2.0",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    async with websockets.connect(websocket_url, ping_interval=timeout_seconds, extra_headers=headers) as websocket:
        print('connected')
        async for message in websocket:
            await on_message(message)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_websocket())
    loop.run_forever()
