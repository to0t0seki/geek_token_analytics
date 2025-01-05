import sys
sys.path.append("/home/ubuntu/geek_analytics_test")
from src.data_processing.adjusted_daily_balances_calculator import calculate_yesterday_balances
from datetime import datetime, timedelta

def daily_1915_utc_update_scheduler():
    current_time = datetime.now() + timedelta(hours=9)
    print(f"start: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("1915 UTCの更新を行います")
    calculate_yesterday_balances()
    print("1915 UTCの更新を行いました")

if __name__ == "__main__":
    daily_1915_utc_update_scheduler()





