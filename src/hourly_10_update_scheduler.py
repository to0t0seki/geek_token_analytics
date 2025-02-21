import traceback
import sys
sys.path.append("/home/ubuntu/geek_analytics_test")

from src.database.importer.geek_transactions_importer import update_geek_transactions
from src.database.importer.equipment_transactions_importer import update_equipment_transactions
from src.database.importer.doll_transactions_importer import update_doll_transactions
from src.database.importer.market_data_importer import update_ohlcv_1h

from src.database.materialized_views.daily_balances import refresh_daily_balances
from src.database.materialized_views.latest_balances import refresh_latest_balances

from src.database.materialized_views.users_addresses import refresh_users_addresses
from src.database.materialized_views.others_addresses import refresh_others_addresses
from src.database.materialized_views.exchange_addresses import refresh_exchange_addresses




from src.database.data_access.database_client import DatabaseClient
from src.logger import setup_logger


logger = setup_logger(__name__)

def hourly_10_update_scheduler():
 
    db_client = DatabaseClient()
    logger.info("start: hourly_10_update_scheduler")

    update_geek_transactions(db_client)
    update_equipment_transactions(db_client)
    update_doll_transactions(db_client)
    update_ohlcv_1h(db_client)

    refresh_daily_balances(db_client)
    refresh_latest_balances(db_client)

    refresh_users_addresses(db_client)
    refresh_others_addresses(db_client)
    refresh_exchange_addresses(db_client)

    logger.info("end: hourly_10_update_scheduler")
  

if __name__ == "__main__":
    try:
        hourly_10_update_scheduler()
    except Exception:
        logger.error(traceback.format_exc())

