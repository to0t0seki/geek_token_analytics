import streamlit as st
import json
import pandas as pd
from src.visualization.components.sidebar import show_sidebar
from src.database.data_access.queries import get_latest_balances_from_all_addresses, get_latest_balances_from_airdrop_recipient, get_latest_balances_from_exchange, get_latest_balances_from_operator, get_address_info, get_jst_4am_close_price
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.visualization.components.chart import display_chart
from src.database.data_access.database_client import DatabaseClient

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")



st.title("個別アドレス情報")

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

# データソースの選択
data_sources = {
    "全てのアドレス": lambda: get_latest_balances_from_all_addresses(st.session_state.db_client),
    "ユーザーアドレス": lambda: get_latest_balances_from_airdrop_recipient(st.session_state.db_client),
    "取引所": lambda: get_latest_balances_from_exchange(st.session_state.db_client),
    "運営": lambda: get_latest_balances_from_operator(st.session_state.db_client),
}

geek_price_df = get_jst_4am_close_price(st.session_state.db_client)
geek_price = float(geek_price_df.iloc[0]['close'])

selected_source = st.selectbox("アドレスのカテゴリーを選択してください:", list(data_sources.keys()))

with st.spinner('データを取得中...'):
    df = data_sources[selected_source]()



df = df[['address', 'balance']]
df.sort_values(by='balance', ascending=False, inplace=True)
df.insert(0, 'No', range(1, len(df) + 1))
df['balance'] = df['balance'].round(0)
df['dollar_base'] = df['balance'] * geek_price
df['Note'] = None

with open("address_notes.json", 'r',encoding='utf-8') as f:
       address_notes = json.load(f)
df['Note'] = df['address'].map(address_notes)
df.rename(columns={'address':'アドレス','balance':'残高(geek)','dollar_base':'残高(dollar)'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single')
gb.configure_column('アドレス', filter=True)
gb.configure_columns(["残高(geek)", "残高(dollar)"],valueFormatter="Math.floor(value).toLocaleString()")


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
st.write("行のフィルタリングやソートも可能です。")

st.write("")
st.write("")


selected_row = grid_response['selected_rows']
if isinstance(selected_row, pd.DataFrame):

    
    st.write(f"選択されたアドレス: {selected_row.iloc[0]['アドレス']}, 備考: {selected_row.iloc[0]['Note']}")
    address_info_df = get_address_info(st.session_state.db_client, selected_row.iloc[0]['アドレス'])
    merged_df = pd.merge(
        address_info_df,
        geek_price_df,
        left_on='date',
        right_on='date',
        how='left'
    )[['date','close', 'balance', 'airdrop', 'withdraw', 'deposit']]

    merged_df['balance_dollar_base'] = merged_df['close'] * merged_df['balance']
    merged_df['airdrop_dollar_base'] = merged_df['close'] * merged_df['airdrop']
    merged_df['withdraw_dollar_base'] = merged_df['close'] * merged_df['withdraw']
    merged_df['deposit_dollar_base'] = merged_df['close'] * merged_df['deposit']

    merged_df['date'] = pd.to_datetime(merged_df['date']).dt.strftime('%Y-%m-%d')
    
    # 複数カラムを一度にround
    merged_df[['balance', 'airdrop', 'withdraw', 'deposit', 
            'balance_dollar_base', 'airdrop_dollar_base', 
            'withdraw_dollar_base', 'deposit_dollar_base']] = \
        merged_df[['balance', 'airdrop', 'withdraw', 'deposit',
                'balance_dollar_base', 'airdrop_dollar_base',
                'withdraw_dollar_base', 'deposit_dollar_base']].round(0)


    merged_df.rename(columns={'date':'日付','balance':'残高(geek)','airdrop':'エアドロ(geek)','withdraw':'出金(geek)','deposit':'入金(geek)'}, inplace=True)
    merged_df.rename(columns={'balance_dollar_base':'残高(dollar)','airdrop_dollar_base':'エアドロ(dollar)','withdraw_dollar_base':'出金(dollar)','deposit_dollar_base':'入金(dollar)'}, inplace=True)
    gb = GridOptionsBuilder.from_dataframe(merged_df)
    gb.configure_columns(["残高(geek)", "エアドロ(geek)", "出金(geek)", "入金(geek)","残高(dollar)","エアドロ(dollar)","出金(dollar)","入金(dollar)"],valueFormatter="Math.floor(value).toLocaleString()")
    gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)

    grid_response = AgGrid(
        merged_df,
        gridOptions=gb.build(),
        height=300,
        width='100%',
        theme='streamlit' ,
        update_mode=GridUpdateMode.NO_UPDATE
    )
    display_chart(
        [merged_df[['日付','残高(dollar)']], 'dollar', 'blue', 'y'],
        [merged_df[['日付','残高(geek)']], 'geek', 'red', 'y2'],
        title="残高推移",
    )

    display_chart(
        [merged_df[['日付','エアドロ(dollar)']], 'dollar', 'blue', 'y'],
        [merged_df[['日付','エアドロ(geek)']], 'geek', 'red', 'y2'],
        title="エアドロップ取得推移",
    )

    display_chart(
        [merged_df[['日付','出金(dollar)']], 'dollar', 'blue', 'y'],
        [merged_df[['日付','出金(geek)']], 'geek', 'red', 'y2'],
        title="出金推移",
    )

    display_chart(
        [merged_df[['日付','入金(dollar)']], 'dollar', 'blue', 'y'],
        [merged_df[['日付','入金(geek)']], 'geek', 'red', 'y2'],
        title="入金推移",
    )




