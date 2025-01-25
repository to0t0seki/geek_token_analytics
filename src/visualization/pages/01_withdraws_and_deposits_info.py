import streamlit as st
from src.visualization.components.chart import display_chart
from src.database.data_access.queries import get_daily_deposits, get_daily_withdrawals, get_jst_4am_close_price
from src.visualization.components.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.database.data_access.database_client import DatabaseClient
import pandas as pd



st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")


st.title("入出金")

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

with st.spinner('データを取得中...'):
    deposits_df = get_daily_deposits(st.session_state.db_client)
    withdrawals_df = get_daily_withdrawals(st.session_state.db_client)



st.write("### 入金")

ohlcv_df = get_jst_4am_close_price(st.session_state.db_client)
merged_deposits_df = pd.merge(
    deposits_df[['date', 'value', 'address_count']],
    ohlcv_df[['date','close']],
    left_on='date',
    right_on='date',
    how='left'
)[['date', 'value', 'close','address_count']]

merged_deposits_df['dollar_base'] = merged_deposits_df['close'] * merged_deposits_df['value']
merged_deposits_df= merged_deposits_df[['date','value','close','dollar_base','address_count']]
merged_deposits_df['value'] = merged_deposits_df['value'].round(0)
merged_deposits_df['dollar_base'] = merged_deposits_df['dollar_base'].round(0)
merged_deposits_df['date'] = pd.to_datetime(merged_deposits_df['date']).dt.strftime('%Y-%m-%d')


merged_deposits_df.rename(columns={'date':'日付','value':'入金枚数','address_count':'ユニークアドレス数','close':'終値','dollar_base':'ドル換算'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(merged_deposits_df)
gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)
gb.configure_columns(
    ["入金枚数", "ユニークアドレス数", "ドル換算"],
    valueFormatter="Math.floor(value).toLocaleString()"
)


grid_response = AgGrid(
    merged_deposits_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE
)

total_deposits = merged_deposits_df['入金枚数'].sum()
total_dollar_base = merged_deposits_df['ドル換算'].sum()
st.markdown(f"総入金枚数: {total_deposits:,.0f} ドル換算: {total_dollar_base:,.0f}")

st.write("")

st.write("### 出金")




merged_withdrawals_df = pd.merge(
    withdrawals_df[['date', 'value', 'address_count']],
    ohlcv_df[['date','close']],
    left_on='date',
    right_on='date',
    how='left'
)[['date', 'value', 'close','address_count']]

merged_withdrawals_df['dollar_base'] = merged_withdrawals_df['close'] * merged_withdrawals_df['value']

merged_withdrawals_df= merged_withdrawals_df[['date','value','close','dollar_base','address_count']]
merged_withdrawals_df['value'] = merged_withdrawals_df['value'].round(0)
merged_withdrawals_df['dollar_base'] = merged_withdrawals_df['dollar_base'].round(0)
merged_withdrawals_df['date'] = pd.to_datetime(merged_withdrawals_df['date']).dt.strftime('%Y-%m-%d')



merged_withdrawals_df.rename(columns={'date':'日付','value':'出金枚数','address_count':'ユニークアドレス数','close':'終値','dollar_base':'ドル換算'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(merged_withdrawals_df)
gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)
gb.configure_columns(
    ["出金枚数", "ユニークアドレス数", "ドル換算"],
    valueFormatter="Math.floor(value).toLocaleString()"
)

grid_response = AgGrid(
    merged_withdrawals_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE
)


total_withdrawals = merged_withdrawals_df['出金枚数'].sum()
total_dollar_base = merged_withdrawals_df['ドル換算'].sum()
st.markdown(f"総出金枚数: {total_withdrawals:,.0f} ドル換算: {total_dollar_base:,.0f}")


display_chart(
    [merged_deposits_df[['日付','ドル換算']],'入金','blue','y'],
    [merged_withdrawals_df[['日付','ドル換算']],'出金','red','y'],
    title='入出金のドル換算推移',
)


