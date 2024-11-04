import pandas as pd
from src.data_access.database import get_daily_xgeek_to_geek

df = get_daily_xgeek_to_geek("data/processed/geek_transfers.db")
print(df.info())
print(df.head())