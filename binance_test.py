from dotenv import load_dotenv
import os
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from datetime import datetime, timedelta, timezone

# load .env variables
load_dotenv()

client = Client(os.environ['API_KEY_OLD'], os.environ['API_SECRET_OLD'], testnet=True, tld='us')

if __name__ == "__main__":

  past_30_days = datetime.now() - timedelta(days=30)
  start_time = int(past_30_days.timestamp() * 1000)

  klines = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1DAY, startTime=start_time, limit=30)

  print(len(klines))
