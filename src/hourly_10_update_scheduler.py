import traceback
import sys
sys.path.append("/home/ubuntu/geek_analytics_test")

from src.database.data_collection.geek_transactions_importer import update_geek_transactions
from src.database.repositorys.daily_balances_repository import refresh_daily_balances
from src.database.repositorys.latest_balances_repository import refresh_latest_balances
from src.database.repositorys.airdrop_recipients_repository import refresh_airdrop_recipients
from src.database.data_collection.market_data_importer import refresh_ohlcv_1h



from src.database.data_access.database_client import DatabaseClient
from src.logger import setup_logger


logger = setup_logger(__name__)

def hourly_10_update_scheduler():
 
    db_client = DatabaseClient()
    logger.info("start: hourly_10_update_scheduler")

    update_geek_transactions(db_client)
    refresh_daily_balances(db_client)
    refresh_latest_balances(db_client)
    refresh_airdrop_recipients(db_client)
    refresh_ohlcv_1h(db_client)

    logger.info("end: hourly_10_update_scheduler")
  

if __name__ == "__main__":
    try:
        hourly_10_update_scheduler()
    except Exception:
        logger.error(traceback.format_exc())

