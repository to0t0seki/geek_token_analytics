import streamlit as st
import json
import pandas as pd
from src.visualization.components.layout.sidebar import show_sidebar
# from src.data_access.database import get_all_balances, get_airdrop_recipient_balances, get_exchange_balances
from src.data_access.query import get_latest_balances_from_all_addresses, get_latest_balances_from_airdrop_recipient, get_latest_balances_from_exchange, get_latest_balances_from_operator, get_address_info
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.visualization.components.charts.chart import display_chart
from src.data_access.client import DatabaseClient

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")



st.title("個別アドレス情報")

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

# データソースの選択
data_sources = {
    "全てのアドレス": lambda: get_latest_balances_from_all_addresses(),
    "エアドロを受け取った事のあるアドレス": lambda: get_latest_balances_from_airdrop_recipient(),
    "取引所": lambda: get_latest_balances_from_exchange(),
    "運営": lambda: get_latest_balances_from_operator(),
}


selected_source = st.selectbox("アドレスのカテゴリーを選択してください:", list(data_sources.keys()))

with st.spinner('データを取得中...'):
    df = data_sources[selected_source]()


df = df[['address', 'balance']]
df['balance'] = df['balance'].round(0)
df['Note'] = None

with open("config/address_notes.json", 'r',encoding='utf-8') as f:
       address_notes = json.load(f)
df['Note'] = df['address'].map(address_notes)
df.rename(columns={'address':'アドレス','balance':'最新残高'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single')
gb.configure_column('アドレス', filter=True)
gb.configure_column("最新残高",valueFormatter="Math.floor(value).toLocaleString()")





grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
)

st.write("行を選択すると残高推移が表示されます。")
st.write("アドレス列ちょいちょいいじるとフィルタリングやソートも可能です。")

st.write("")
st.write("")


selected_row = grid_response['selected_rows']
if isinstance(selected_row, pd.DataFrame):
    st.write(f"選択されたアドレス: {selected_row.iloc[0]['アドレス']}, 備考: {selected_row.iloc[0]['Note']}")
    address_info_df = get_address_info(selected_row.iloc[0]['アドレス'])
    
    address_info_df['balance'] = address_info_df['balance'].round(0)
    address_info_df['airdrop'] = address_info_df['airdrop'].round(0)
    address_info_df['withdraw'] = address_info_df['withdraw'].round(0)
    address_info_df['deposit'] = address_info_df['deposit'].round(0)
    address_info_df.rename(columns={'date':'日付','balance':'残高','airdrop':'エアドロップ','withdraw':'出金','deposit':'入金'}, inplace=True)

    gb = GridOptionsBuilder.from_dataframe(address_info_df)
    gb.configure_columns(["残高", "エアドロップ", "出金", "入金"],valueFormatter="Math.floor(value).toLocaleString()")
    gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)

    grid_response = AgGrid(
        address_info_df,
        gridOptions=gb.build(),
        height=300,
        width='100%',
        theme='streamlit' ,
        update_mode=GridUpdateMode.NO_UPDATE
    )
    address_info_df_tmp = address_info_df[['日付', '残高']]

    display_chart(
        address_info_df_tmp,
        title="残高推移",
        chart_type='line',
        legend_name='残高',
    )

    address_info_df_tmp = address_info_df[['日付', 'エアドロップ']]

    display_chart(
        address_info_df_tmp,
        title="エアドロップ取得推移",
        chart_type='line',
        legend_name='エアドロップ',
    )

    address_info_df_tmp = address_info_df[['日付', '出金']]

    display_chart(
        address_info_df_tmp,
        title="出金推移",
        chart_type='line',
        legend_name='出金',
    )

    address_info_df_tmp = address_info_df[['日付', '入金']]

    display_chart(
        address_info_df_tmp,
        title="入金推移",
        chart_type='line',
        legend_name='入金',
    )


