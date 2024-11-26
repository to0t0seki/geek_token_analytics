import streamlit as st
import json
import pandas as pd
from src.visualization.components.layout.sidebar import show_sidebar
# from src.data_access.database import get_all_balances, get_airdrop_recipient_balances, get_exchange_balances
from src.data_access.query import get_latest_balances_from_all_addresses, get_latest_balances_from_airdrop_recipient, get_latest_balances_from_exchange, get_latest_balances_from_operator, get_address_info
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.visualization.components.charts.chart import display_chart

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()


st.title("個別アドレスの残高")

# データソースの選択
data_sources = {
    "全てのアドレス": lambda: get_latest_balances_from_all_addresses(),
    "エアドロを受け取った事のあるアドレス": lambda: get_latest_balances_from_airdrop_recipient(),
    "取引所": lambda: get_latest_balances_from_exchange(),
    "運営": lambda: get_latest_balances_from_operator(),
}


selected_source = st.selectbox("アドレスのカテゴリーを選択してください:", list(data_sources.keys()))
df = data_sources[selected_source]()


df = df[['address', 'balance']]
df['balance'] = df['balance'].round(0)
df['Note'] = None

with open("config/address_notes.json", 'r',encoding='utf-8') as f:
       address_notes = json.load(f)
df['Note'] = df['address'].map(address_notes)

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single')
gb.configure_column('address', filter=True)
# gb.configure_default_column(filterable=True)

column_names = {
    'address': 'アドレス',
    'balance': '最新残高',
}

for col_name, jp_name in column_names.items():
    gb.configure_column(
        col_name,
        header_name=jp_name,
    )

grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
)

st.write("行を選択すると残高推移が表示されます。")
st.write("アドレス列の三本線からフィルタリングも可能です。")
st.write("")
st.write("")


selected_row = grid_response['selected_rows']
if isinstance(selected_row, pd.DataFrame):
    st.write(f"選択されたアドレス: {selected_row.iloc[0]['address']}, 備考: {selected_row.iloc[0]['Note']}")
    address_info_df = get_address_info(selected_row.iloc[0]['address'])
    
    address_info_df['balance'] = address_info_df['balance'].round(0)
    address_info_df['airdrop'] = address_info_df['airdrop'].round(0)
    address_info_df['withdraw'] = address_info_df['withdraw'].round(0)
    address_info_df['deposit'] = address_info_df['deposit'].round(0)

    gb = GridOptionsBuilder.from_dataframe(address_info_df)
    
  

    column_names = {
        'date': '日付',
        'balance': '残高',
        'airdrop': 'エアドロ',
        'withdraw': '出金',
        'deposit': '入金',
    }


    for col_name, jp_name in column_names.items():
        gb.configure_column(
            col_name,
            header_name=jp_name,
    )

    grid_response = AgGrid(
        address_info_df,
        gridOptions=gb.build(),
        height=300,
        width='100%',
        theme='streamlit' ,
        update_mode=GridUpdateMode.NO_UPDATE
    )
    address_info_df = address_info_df[['date', 'balance']]

    display_chart(
        address_info_df,
        title="推移",
    )
