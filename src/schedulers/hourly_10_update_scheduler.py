import sys
sys.path.append("/home/ubuntu/geek_analytics_test")
from src.data_collection.geek_transactions_importer import get_geek_data
from datetime import datetime, timedelta
from src.data_collection.market_data_importer import fetch_ohlcv
from src.data_processing.daily_balances_creater import refresh_daily_balances
from src.data_processing.airdrop_recipients_creator import refresh_airdrop_recipients
from src.data_processing.latest_balances_creator import refresh_latest_balances
from src.data_access.client import DatabaseClient

def hourly_10_update_scheduler():
    current_time = datetime.now() + timedelta(hours=9)
    print(f"start: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("10分の更新を行います")
    get_geek_data()
    refresh_daily_balances()
    refresh_latest_balances()
    refresh_airdrop_recipients()

    client = DatabaseClient()
    fetch_ohlcv(client)
    

    print("10分の更新を行いました")

if __name__ == "__main__":
    hourly_10_update_scheduler()

