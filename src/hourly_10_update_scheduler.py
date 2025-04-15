import traceback
from src.database.importer.geek_transactions_importer import update_geek_transactions
from src.database.importer.geek_transactions_oas_importer import update_geek_transactions as update_geek_transactions_oas
from src.database.importer.equipment_transactions_importer import update_equipment_transactions
from src.database.importer.doll_transactions_importer import update_doll_transactions
from src.database.importer.ohlcv_importer import update_ohlcv_1h

import sys
sys.path.append("/home/ubuntu/geek_token_analytics")

from tools.remove_reorg_records import cleanup_reorg_records
from tools.exchange_address_checker import check_exchange_address
from src.database.materialized_views.daily_balances import refresh_daily_balances
from src.database.materialized_views.latest_balances import refresh_latest_balances
from src.database.materialized_views.addresses import refresh_addresses





from src.database.data_access.database_client import DatabaseClient
from src.logger import setup_logger


logger = setup_logger(__name__)

def hourly_10_update_scheduler():
 
    db_client = DatabaseClient()
    logger.info("hourly_10_update_schedulerを開始します")

    #データの取得
    update_geek_transactions(db_client)
    update_geek_transactions_oas(db_client)
    update_equipment_transactions(db_client)
    update_doll_transactions(db_client)
    update_ohlcv_1h(db_client)

    #データチェック
    cleanup_reorg_records(db_client)
    check_exchange_address(db_client)

    #マテリアライズドビューの更新
    refresh_daily_balances(db_client)
    refresh_addresses(db_client)
    refresh_latest_balances(db_client)

    logger.info("hourly_10_update_schedulerを終了します")
  

if __name__ == "__main__":
    try:
        hourly_10_update_scheduler()
    except Exception:
        logger.error(traceback.format_exc())

