from src.data_processing.adjusted_daily_balances_calculator import calculate_yesterday_balances
from src.data_collection.market_data_importer import import_market_data

def daily_1905_utc_update_scheduler():
    print("1905 UTCの更新を行います")
    calculate_yesterday_balances()
    import_market_data()
    print("1905 UTCの更新を行いました")

if __name__ == "__main__":
    daily_1905_utc_update_scheduler()





