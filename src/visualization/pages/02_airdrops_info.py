import streamlit as st
from src.visualization.components.chart import display_chart
from src.database.data_access.queries import get_daily_airdrops, get_jst_4am_close_price
from src.visualization.components.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.database.data_access.database_client import DatabaseClient
import pandas as pd



st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")



st.title(f"エアドロップ")

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

with st.spinner('データを取得中...'):
    airdrops_df = get_daily_airdrops(st.session_state.db_client)



st.write("日次エアドロップ")
ohlcv_df = get_jst_4am_close_price(st.session_state.db_client)

merged_airdrops_df = pd.merge(
    airdrops_df[['date', 'value', 'address_count']],
    ohlcv_df[['date','close']],
    left_on='date',
    right_on='date',
    how='left'
)[['date', 'value', 'close','address_count']]

merged_airdrops_df['dollar_base'] = merged_airdrops_df['close'] * merged_airdrops_df['value']
merged_airdrops_df= merged_airdrops_df[['date','value','close','dollar_base','address_count']]
merged_airdrops_df['value'] = merged_airdrops_df['value'].round(0)
merged_airdrops_df['dollar_base'] = merged_airdrops_df['dollar_base'].round(0)
merged_airdrops_df['date'] = pd.to_datetime(merged_airdrops_df['date']).dt.strftime('%Y-%m-%d')

merged_airdrops_df.rename(columns={'date':'日付','value':'エアドロップ枚数','address_count':'ユニークアドレス数','close':'終値','dollar_base':'ドル換算'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(merged_airdrops_df)
gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)
gb.configure_columns(
    ["エアドロップ枚数", "ユニークアドレス数", "ドル換算"],
    valueFormatter="Math.floor(value).toLocaleString()"
)

grid_response = AgGrid(
    merged_airdrops_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE,
)


total_airdrops = merged_airdrops_df['エアドロップ枚数'].sum()
total_dollar_base = merged_airdrops_df['ドル換算'].sum()
st.markdown(f"総エアドロップ枚数: {total_airdrops:,.0f} ドル換算: {total_dollar_base:,.0f}")




display_chart(
    [merged_airdrops_df[['日付','ドル換算']],'ドル換算','blue','y'],
    [merged_airdrops_df[['日付','エアドロップ枚数']],'枚数','red','y2'],
    title='エアドロップのドル換算推移',
)