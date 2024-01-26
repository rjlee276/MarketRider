import os
import time
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, CryptoLatestQuoteRequest
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopLossRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import CryptoDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce , OrderType
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()

# CONSTANTS
PAPER_KEY = os.getenv('PAPER_KEY')
PAPER_SECRET = os.getenv('PAPER_SECRET')
SYMBOL = 'BTC/USD'


# PARAMETERS FOR TRADING
LONG = timedelta(days=30)
SHORT = timedelta(days=27)
RISK_PERCENT = 1
STOP_LOSS = 2
STOP_LOSS_PRICE = float('inf')
STOP_LOSS_SHARES = 0

RUNNING_SHORT_SMA = []
RUNNING_LONG_SMA = []

trading_client = TradingClient(PAPER_KEY, PAPER_SECRET, paper=True)
account = trading_client.get_account()
client = CryptoHistoricalDataClient()
buy_in_shares = 1

def wait_for_next_minute():
    """Wait until the start of the next minute."""
    now = datetime.now()
    # Calculate the number of seconds until the next minute
    seconds_to_wait = 60 - now.second + (10**6 - now.microsecond) / 10**6
    time.sleep(seconds_to_wait)

while True:
    wait_for_next_minute()
    print(f'Total Cash Balance: ${account.cash}')
    request_params = CryptoLatestQuoteRequest(symbol_or_symbols="BTC/USD")
    current_price = client.get_crypto_latest_quote(request_params)[SYMBOL].ask_price
    print(f'Current {SYMBOL} Price: ${current_price}')
    current_date = datetime.now()

    # SHORT SMA
    request_params = CryptoBarsRequest(symbol_or_symbols=[SYMBOL], timeframe=TimeFrame.Minute, start=current_date-SHORT, end=current_date)
    short_sma_bars = client.get_crypto_bars(request_params).data[SYMBOL]

    short_sma = sum(item.close for item in short_sma_bars) / len(short_sma_bars)
    print(f'Current Short SMA: {short_sma}')


    request_params = CryptoBarsRequest(symbol_or_symbols=[SYMBOL], timeframe=TimeFrame.Minute, start=current_date-LONG, end=current_date-SHORT)
    long_sma_bars = client.get_crypto_bars(request_params).data[SYMBOL]

    long_sma = sum(item.close for item in long_sma_bars) / len(long_sma_bars)
    print(f'Current Long SMA: {long_sma}')

    RUNNING_SHORT_SMA.append(short_sma)
    RUNNING_LONG_SMA.append(long_sma)

    if len(RUNNING_LONG_SMA) < 2 or len(RUNNING_SHORT_SMA) < 2:
        print('----------No Previous Data, Waiting for next minute----------')
        continue

    if current_price < STOP_LOSS_PRICE:
        print(f'----------Selling {SYMBOL} Due To Stop Loss----------')
        market_order_data = MarketOrderRequest(symbol=SYMBOL, qty=STOP_LOSS_SHARES, side=OrderSide.SELL, time_in_force=TimeInForce.GTC)
        market_order = trading_client.submit_order(order_data=market_order_data) 
        STOP_LOSS_PRICE = float('inf')
        STOP_LOSS_SHARES = 0
  

    # SHORT SMA goes UNDER LONG SMA, we sell
    if RUNNING_SHORT_SMA[-2] > RUNNING_LONG_SMA[-2] and RUNNING_SHORT_SMA[-1] < RUNNING_LONG_SMA[-1]:
        print(f'----------Selling {SYMBOL}----------')
        trading_client.close_all_positions()
        continue
        
    
    # SHORT SMA goes OVER LONG SMA, we BUY
    if RUNNING_SHORT_SMA[-2] < RUNNING_LONG_SMA[-2] and  RUNNING_SHORT_SMA[-1] > RUNNING_LONG_SMA[-1]:
        print(f'----------Buying {SYMBOL}----------')
        STOP_LOSS_PRICE = current_price * (1 - (STOP_LOSS/100))
        buy_in_dollars = account.cash * (RISK_PERCENT / 100)
        buy_in_shares = buy_in_dollars/current_price
        STOP_LOSS_SHARES = buy_in_shares

        market_order_data = MarketOrderRequest(symbol=SYMBOL, qty=buy_in_shares, side=OrderSide.BUY, time_in_force=TimeInForce.GTC)
        market_order = trading_client.submit_order(order_data=market_order_data)  
        continue  
        
    print('----------No Activity----------')
    

# For websocket
"""
crypto_stream = CryptoDataStream(api_key, secret_key)

async def quote_data_handler(data):
    # quote data will arrive here
    print(data.ask_price)

crypto_stream.subscribe_quotes(quote_data_handler, "BTC/USD")

crypto_stream.run()
"""