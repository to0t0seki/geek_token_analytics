import streamlit as st
import plotly.express as px
import pandas as pd
from src.database.data_access.queries import (get_latest_balances_from_game_ops_wallet,
                                                get_latest_balances_from_airdrop_wallet,
                                                 get_latest_balances_from_withdrawal_wallet,
                                                   get_latest_balances_from_exchange,
                                                     get_latest_balances_from_others,
                                                       get_latest_balances_from_users,
                                                         get_latest_balances_from_item_wallet)
from src.visualization.components.layout import initialize_page



st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

initialize_page()

style = '''
<style>
.stApp {
    background-image: url('https://lastmemories.io/special/assets/fankit-assets/PC/01_5_komari.jpg');
    background-size: cover;
    background-repeat: no-repeat;}
.stCustomComponentV1 {
       max-width: 70% !important;
    }
.main-svg {
  background: transparent !important;
}
</style>
'''
st.markdown(style, unsafe_allow_html=True)

st.title(f"ホルダー分布")


with st.spinner('データを取得中...'):
    operators_balances = get_latest_balances_from_game_ops_wallet(st.session_state.db_client)
    airdrop_wallet_balances = get_latest_balances_from_airdrop_wallet(st.session_state.db_client)
    withdrawal_wallet_balances = get_latest_balances_from_withdrawal_wallet(st.session_state.db_client)
    users_addresses_balances = get_latest_balances_from_users(st.session_state.db_client)
    exchanges_balances = get_latest_balances_from_exchange(st.session_state.db_client)
    other_holders_balances = get_latest_balances_from_others(st.session_state.db_client)
    item_wallet_balances = get_latest_balances_from_item_wallet(st.session_state.db_client)





category_totals = pd.DataFrame([
    {
        '名前': '運営',
        '枚数': operators_balances['balance'].sum().round(0)
    },
        {
        '名前': 'エアドロップウォレット',
        '枚数': airdrop_wallet_balances['balance'].sum().round(0)
    },
        {
        '名前': '出金ウォレット',
        '枚数': withdrawal_wallet_balances['balance'].sum().round(0)
    },
    {
        '名前': 'ユーザー',
        '枚数': users_addresses_balances['balance'].sum().round(0)
    },
    {
        '名前': '取引所',
        '枚数': exchanges_balances['balance'].sum().round(0)
    },
    {
        '名前': 'その他',
        '枚数': other_holders_balances['balance'].sum().round(0)
    },
    {
        '名前': 'Geekショップ用ウォレット',
        '枚数': item_wallet_balances['balance'].sum().round(0)
    }
])
# 円グラフの作成
fig = px.pie(
    category_totals,
    values='枚数', 
    names='名前', 
    # title='GEEKトークン保有者分布'
    )
fig.update_traces(textposition='inside', textinfo='percent+label')


# グラフの表示
st.plotly_chart(fig, use_container_width=True)

# 総供給量の計算と表示
total_supply = category_totals['枚数'].sum()
st.write(f"現在の総供給量: {total_supply:,.0f}")


st.markdown("""
###### ホルダーの説明
- 運営:0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62
- エアドロップウォレット:0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7
- 出金ウォレット:0x687F3413C7f0e089786546BedF809b8F8885B051
- Geekショップ用ウォレット:0x188b3678a4E706D17D060E6FCFbfec359e4bb69a
- ユーザー:エアドロップを一度でも受け取った事のあるアドレス
- 取引所
    - Bitget:0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23
    - Gate.io:0x0D0707963952f2fBA59dD06f2b425ace40b492Fe
- その他:上記以外のウォレット
""")
