import streamlit as st
from src.visualization.components.charts.chart import display_chart1
from src.data_access.query import get_daily_deposits, get_daily_withdrawals
from src.visualization.components.layout.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.data_access.client import DatabaseClient
import pandas as pd



st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")


st.title("入出金")

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

with st.spinner('データを取得中...'):
    deposits_df = get_daily_deposits()
    withdrawals_df = get_daily_withdrawals()


st.write("### 入金")
deposits_df['per_address'] = deposits_df['per_address'].round(0)
deposits_df['value'] = deposits_df['value'].round(0)
deposits_df['date'] = pd.to_datetime(deposits_df['date']).dt.strftime('%Y-%m-%d')




deposits_df.rename(columns={'date':'日付','value':'入金枚数','address_count':'ユニークアドレス数','per_address':'平均'}, inplace=True)


gb = GridOptionsBuilder.from_dataframe(deposits_df)
gb.configure_columns(
    ["入金枚数", "ユニークアドレス数", "平均"],
    # type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
    valueFormatter="Math.floor(value).toLocaleString()"
)
gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)

grid_response = AgGrid(
    deposits_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE
)

total_deposits = deposits_df['入金枚数'].sum()
st.write(f"総入金枚数: {total_deposits:,.0f}")

st.write("")

st.write("### 出金")
withdrawals_df['per_address'] = withdrawals_df['per_address'].round(0)
withdrawals_df['value'] = withdrawals_df['value'].round(0)
withdrawals_df['date'] = pd.to_datetime(withdrawals_df['date']).dt.strftime('%Y-%m-%d')


withdrawals_df.rename(columns={'date':'日付','value':'出金枚数','address_count':'ユニークアドレス数','per_address':'平均'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(withdrawals_df)
gb.configure_columns(
    ["出金枚数", "ユニークアドレス数", "平均"],
    valueFormatter="Math.floor(value).toLocaleString()"
)
gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)


grid_response = AgGrid(
    withdrawals_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE
)


total_withdrawals = withdrawals_df['出金枚数'].sum()
st.write(f"総出金枚数: {total_withdrawals:,.0f}")


withdrawals_df.drop(withdrawals_df.columns[2:4], axis=1, inplace=True)
deposits_df.drop(deposits_df.columns[2:4], axis=1, inplace=True)

display_chart1(
    deposits_df,
    withdrawals_df,
)

