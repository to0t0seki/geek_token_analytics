from src.data_collection.geek_transaction_importer import get_geek_data, calculate_todays_balances
from datetime import datetime, timedelta

def hourly_10_update_scheduler():
    current_time = datetime.now() + timedelta(hours=9)
    print(f"start: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    get_geek_data()
    calculate_todays_balances()
    print("10分の更新を行いました")

if __name__ == "__main__":
    hourly_10_update_scheduler()

