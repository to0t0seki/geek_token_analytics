import sys
sys.path.append("/home/ubuntu/geek_analytics_test")
import time
from src.data_collection.geek_transaction_importer import get_geek_data, calculate_todays_balances

def hourly_10_update_scheduler():
    print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("10分の更新を行います")
    get_geek_data()
    calculate_todays_balances()
    print("10分の更新を行いました")

if __name__ == "__main__":
    hourly_10_update_scheduler()

