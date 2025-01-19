import streamlit as st
import pandas as pd
from src.visualization.components.chart import display_supply_and_price_chart
from src.data_access.query import get_airdrop_recipient_balances, get_jst_4am_close_price
from src.visualization.components.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.data_access.client import DatabaseClient
import pandas as pd


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")


st.title("ユーザー残高")
st.write("・終値はBITGETのJST3時終値の値。")


if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

with st.spinner('データを取得中...'):
    daily_total_balances_df = get_airdrop_recipient_balances()



ohlcv_df = get_jst_4am_close_price()


merged_df = pd.merge(
    daily_total_balances_df,
    ohlcv_df[['date','close']],
    left_on='date',
    right_on='date',
    how='left'
)[['date', 'balance', 'close']]

merged_df['doll_base'] = merged_df['balance'] * merged_df['close']
merged_df['date'] = pd.to_datetime(merged_df['date']).dt.strftime('%Y-%m-%d')

merged_df.rename(columns={'date':'日付','balance':'保有枚数','close':'終値','doll_base':'ドル換算'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(merged_df)

gb.configure_column('保有枚数',valueFormatter="Math.floor(value).toLocaleString()")
# gb.configure_column('終値',valueFormatter="Math.floor(value).toLocaleString()")
gb.configure_column('ドル換算',valueFormatter="Math.floor(value).toLocaleString()")
gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)

grid_response = AgGrid(
    merged_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE,
)


display_supply_and_price_chart(
    merged_df[['日付','保有枚数','ドル換算']],
    title='保有枚数とドル換算の推移',
)
