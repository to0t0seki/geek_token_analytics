from src.database.views.airdrops_views import create_vw_airdrops
from src.database.views.deposits_views import create_vw_deposits
from src.database.views.withdrawals_views import create_vw_withdrawals
from src.database.views.all_transactions_views import create_vw_all_transactions


from src.database.materialized_views.daily_balances import create_daily_balances
from src.database.materialized_views.latest_balances import create_latest_balances
from src.database.materialized_views.users_addresses import create_users_addresses
from src.database.materialized_views.others_addresses import create_others_addresses
from src.database.materialized_views.exchange_addresses import create_exchange_addresses

from src.database.views.users_balances_views import create_vw_users_balances
from src.database.views.others_balances_views import create_vw_others_balances
from src.database.views.others_transactions_views import create_vw_others_transactions


from src.database.data_access.database_client import DatabaseClient


db_client = DatabaseClient()


create_vw_airdrops(db_client)
create_vw_deposits(db_client)
create_vw_withdrawals(db_client)


# create_daily_balances(db_client)
# create_latest_balances(db_client)
create_users_addresses(db_client)
create_others_addresses(db_client)
create_exchange_addresses(db_client)


create_vw_users_balances(db_client)
create_vw_others_balances(db_client)
create_vw_others_transactions(db_client)


