from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, CryptoLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import CryptoDataStream 
from datetime import datetime, timedelta

long_period = 30
short_period = 27

# No keys required for crypto data
client = CryptoHistoricalDataClient()

while True:
    request_params = CryptoLatestQuoteRequest(symbol_or_symbols="BTC/USD")

    latest_quote = client.get_crypto_latest_quote(request_params)

    # must use symbol to access even though it is single symbol
    short_period_tot = latest_quote["BTC/USD"].ask_price

    day = timedelta(days=1)
    now = datetime.now() - day
    minute= timedelta(minutes=5)

    # Creating request object
    for x in range(short_period-1):
        print(now)
        request_params = CryptoBarsRequest(
                                symbol_or_symbols=["BTC/USD"],
                                timeframe=TimeFrame.Minute,
                                start=now-minute,
                                end=now
                                )

        # Retrieve daily bars for Bitcoin in a DataFrame and printing it
        btc_bars = client.get_crypto_bars(request_params)

        # Convert to dataframe
        short_period_tot += btc_bars.data['BTC/USD'][0].close
        now = now - day

    long_period_tot = short_period_tot

    for x in range(long_period - short_period):
        request_params = CryptoBarsRequest(
                                symbol_or_symbols=["BTC/USD"],
                                timeframe=TimeFrame.Minute,
                                start=now-minute,
                                end=now
                                )

        # Retrieve daily bars for Bitcoin in a DataFrame and printing it
        btc_bars = client.get_crypto_bars(request_params)

        # Convert to dataframe
        long_period_tot += btc_bars.data['BTC/USD'][0].close
        now = now - day
    
    short_sma = short_period_tot / short_period
    long_sma = long_period_tot / long_period

    print(short_sma)
    print(long_sma)

    if short_sma > long_sma:
        pass
  

# For websocket
"""
crypto_stream = CryptoDataStream(api_key, secret_key)

async def quote_data_handler(data):
    # quote data will arrive here
    print(data.ask_price)

crypto_stream.subscribe_quotes(quote_data_handler, "BTC/USD")

crypto_stream.run()
"""