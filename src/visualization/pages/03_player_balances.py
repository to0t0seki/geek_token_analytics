import streamlit as st
import pandas as pd
from src.visualization.components.charts.chart import display_supply_and_price_chart
from src.data_access.query import get_airdrop_recipient_balances, get_jst_4am_close_price
from src.visualization.components.layout.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()


st.title("プレイヤー残高")
st.write("・一度でもエアドロップを受け取ったことのあるアドレスの残高合計。")
st.write("・日付の区切りをJST4時としてあるため、価格は次の日のJST3時の終値。例：10/01の価格は10/02の04:00JSTの価格。")
st.write("・価格はBITGET。")
st.write("・時価総額は<span style='color: red;'>プレイヤーが持っている時価総額</span>としています。計算：合計枚数×価格。",unsafe_allow_html=True)
st.write("・最新価格の更新はJST4時。")
# st.write("・<span style='color: red;'>作ったばかりなので、エラーがあるかも知れません。</span>",unsafe_allow_html=True)



daily_total_balances_df = get_airdrop_recipient_balances()
grouped_df = daily_total_balances_df.groupby(level=1).sum()
grouped_df = grouped_df[grouped_df.index > '2024-09-26']
grouped_df.reset_index(inplace=True)




ohlcv_df = get_jst_4am_close_price()
ohlcv_df['timestamp'] = pd.to_datetime(ohlcv_df['timestamp'].astype(int),unit='ms').dt.floor('D')

merged_df = pd.merge(
    grouped_df[['date', 'balance']],
    ohlcv_df[['timestamp','close']],
    left_on='date',
    right_on='timestamp',
    how='left'
)[['date', 'balance', 'close']]

merged_df['market_cap'] = (merged_df['balance'] * merged_df['close'])
merged_df.sort_values(by='date',ascending=False,inplace=True)
merged_df['date'] = merged_df['date'].dt.strftime('%Y-%m-%d')

merged_df.rename(columns={'date':'日付','balance':'合計枚数','close':'GEEK価格','market_cap':'時価総額'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(merged_df)

gb.configure_column('合計枚数',valueFormatter="Math.floor(value).toLocaleString()")
gb.configure_column('時価総額',valueFormatter="Math.floor(value).toLocaleString()")
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
    merged_df,
    title='合計枚数とプレイヤー時価総額',
)
