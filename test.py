from src.database.data_access.queries.queries import get_latest_balances
from src.database.data_access.database_client import DatabaseClient

df=get_latest_balances(DatabaseClient())
result = df[df['address'] != '0x0000000000000000000000000000000000000000']['balance'].sum()
print(result)

df2 = df[df['sub_type'] == 'main_wallet']['address']
print(df2.info())
print(df2.head(10))   
