import sys
sys.path.append("/home/ubuntu/geek_analytics_test")
from src.data_collection.geek_transaction_importer import get_geek_data
from src.data_processing.adjusted_daily_balances_calculator import calculate_todays_balances
from datetime import datetime, timedelta
from src.data_collection.market_data_importer import fetch_ohlcv

def hourly_10_update_scheduler():
    current_time = datetime.now() + timedelta(hours=9)
    print(f"start: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("10分の更新を行います")
    get_geek_data()
    calculate_todays_balances()
    fetch_ohlcv()

    print("10分の更新を行いました")

if __name__ == "__main__":
    hourly_10_update_scheduler()

