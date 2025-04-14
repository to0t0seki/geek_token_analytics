from src.database.importer.geek_transactions_importer import update_geek_transactions
from src.database.materialized_views.addresses import refresh_addresses
from src.database.data_access.database_client import DatabaseClient

def hourly_10_update_scheduler(db_client: DatabaseClient):
    update_geek_transactions(db_client)
    refresh_addresses(db_client)
if __name__ == "__main__":
    hourly_10_update_scheduler(DatabaseClient())

