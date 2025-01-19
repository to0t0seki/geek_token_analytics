import streamlit as st
import json
import pandas as pd
from src.visualization.components.sidebar import show_sidebar
from src.data_access.query import get_latest_balances_from_all_addresses, get_latest_balances_from_airdrop_recipient, get_latest_balances_from_exchange, get_latest_balances_from_operator, get_address_info, get_jst_4am_close_price
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.visualization.components.chart import display_chart
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
    "ユーザーアドレス": lambda: get_latest_balances_from_airdrop_recipient(),
    "取引所": lambda: get_latest_balances_from_exchange(),
    "運営": lambda: get_latest_balances_from_operator(),
}

geek_price_df = get_jst_4am_close_price()
geek_price = float(geek_price_df.iloc[0]['close'])

selected_source = st.selectbox("アドレスのカテゴリーを選択してください:", list(data_sources.keys()))

with st.spinner('データを取得中...'):
    df = data_sources[selected_source]()



df = df[['address', 'balance']]
df['balance'] = df['balance'].round(0)
df['doll_base'] = df['balance'] * geek_price
df['Note'] = None

with open("config/address_notes.json", 'r',encoding='utf-8') as f:
       address_notes = json.load(f)
df['Note'] = df['address'].map(address_notes)
df.rename(columns={'address':'アドレス','balance':'残高(geek枚数)','doll_base':'残高(ドル換算)'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single')
gb.configure_column('アドレス', filter=True)
gb.configure_columns(["残高(geek枚数)", "残高(ドル換算)"],valueFormatter="Math.floor(value).toLocaleString()")


st.write(f"現在のgeek価格: {geek_price}ドル")


grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    key='address_grid'
)

st.write("行を選択すると残高推移が表示されます。")
st.write("アドレス列ちょいちょいいじるとフィルタリングやソートも可能です。")

st.write("")
st.write("")


selected_row = grid_response['selected_rows']
if isinstance(selected_row, pd.DataFrame):

    
    st.write(f"選択されたアドレス: {selected_row.iloc[0]['アドレス']}, 備考: {selected_row.iloc[0]['Note']}")
    address_info_df = get_address_info(selected_row.iloc[0]['アドレス'])
    merged_df = pd.merge(
        address_info_df,
        geek_price_df,
        left_on='date',
        right_on='date',
        how='left'
    )[['date','close', 'balance', 'airdrop', 'withdraw', 'deposit']]

    merged_df['balance_doll_base'] = merged_df['close'] * merged_df['balance']
    merged_df['airdrop_doll_base'] = merged_df['close'] * merged_df['airdrop']
    merged_df['withdraw_doll_base'] = merged_df['close'] * merged_df['withdraw']
    merged_df['deposit_doll_base'] = merged_df['close'] * merged_df['deposit']

    merged_df['date'] = pd.to_datetime(merged_df['date']).dt.strftime('%Y-%m-%d')
    
    # 複数カラムを一度にround
    merged_df[['balance', 'airdrop', 'withdraw', 'deposit', 
            'balance_doll_base', 'airdrop_doll_base', 
            'withdraw_doll_base', 'deposit_doll_base']] = \
        merged_df[['balance', 'airdrop', 'withdraw', 'deposit',
                'balance_doll_base', 'airdrop_doll_base',
                'withdraw_doll_base', 'deposit_doll_base']].round(0)


    merged_df.rename(columns={'date':'日付','balance':'残高(geek)','airdrop':'エアドロ(geek)','withdraw':'出金(geek)','deposit':'入金(geek)   '}, inplace=True)
    merged_df.rename(columns={'balance_doll_base':'残高(doll)','airdrop_doll_base':'エアドロ(doll)','withdraw_doll_base':'出金(doll)','deposit_doll_base':'入金(doll)'}, inplace=True)
    gb = GridOptionsBuilder.from_dataframe(merged_df)
    gb.configure_columns(["残高(geek)", "エアドロ(geek)", "出金(geek)", "入金(geek)","残高(doll)","エアドロ(doll)","出金(doll)","入金(doll)"],valueFormatter="Math.floor(value).toLocaleString()")
    gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)

    grid_response = AgGrid(
        merged_df,
        gridOptions=gb.build(),
        height=300,
        width='100%',
        theme='streamlit' ,
        update_mode=GridUpdateMode.NO_UPDATE
    )
    address_info_df_tmp = merged_df[['日付', '残高(doll)']]

    display_chart(
        address_info_df_tmp,
        title="残高推移",
        chart_type='line',
        legend_name='残高',
    )

    address_info_df_tmp = merged_df[['日付', 'エアドロ(doll)']]

    display_chart(
        address_info_df_tmp,
        title="エアドロップ取得推移",
        chart_type='line',
        legend_name='エアドロップ',
    )

    address_info_df_tmp = merged_df[['日付', '出金(doll)']]

    display_chart(
        address_info_df_tmp,
        title="出金推移",
        chart_type='line',
        legend_name='出金',
    )

    address_info_df_tmp = merged_df[['日付', '入金(doll)']]

    display_chart(
        address_info_df_tmp,
        title="入金推移",
        chart_type='line',
        legend_name='入金',
    )


