# AlgoTrading

This project is focused on developing an Algo Trading Software using Uplink-API, Websockets, etc.

## Disclaimer

**Important:** This project is intended solely for educational purposes and should not be utilized with real currency.

## About

This project utilizes the UPlink API to create a websocket connection with market data and portfolio data. Key components include:

- Using the API provided by Uplink.
- Enabling the coding of multiple trading strategies in the `exit_strategy.py` file.

## How to Use

Follow these steps to use the AlgoTrading software:

1. Create a `config.cfg` file in the main folder with the following format:

```ini
[INDEX]
api_key =
secret_key =
url = https://127.0.0.1:5000/
websocket_url = wss://api-v2.upstox.com/feed/market-data-feed
portfoliosocket_url = wss://api-v2.upstox.com/feed/portfolio-stream-feed


2. Run `docker-compose up`.
3. A Jupyter notebook will be started.
4. Open `1-Uplink-driver.ipynb` file.
5. Generate the authentication token from the steps mentioned.
6. Generate `MarketDataFeed_pb2.py` from `MarketDataFeed.proto`, as given in the code.
7. Open a terminal and get inside the container using `docker exec -it container_id /bin/bash`.
8. Start the websocket as given in `market_socket.py` for up to 3 stocks or indices.

Feel free to adjust the wording further to suit your specific context and tone. Save this content in a Markdown (.md) file for use as your project's README.
>>>>>>> fc3acab (Trading Logic Updated)
