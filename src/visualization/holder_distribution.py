import streamlit as st
import plotly.express as px
import pandas as pd
from src.database.data_access.queries.queries import get_latest_balances
from src.database.data_access.database_client import DatabaseClient
from src.visualization.components.content import initialize_page


if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

initialize_page(is_top=True)


st.title(f"ホルダー分布")


with st.spinner('データを取得中...'):
    latest_balances = get_latest_balances(st.session_state.db_client)

latest_balances['balance'] = (latest_balances['balance'].astype(float) /1e18).astype(int)





category_totals = pd.DataFrame([
    {
        '名前': '運営',
        '枚数': latest_balances[latest_balances['sub_type']=='main_wallet']['balance'].iloc[0].round(0)
    },
        {
        '名前': 'エアドロップウォレット',
        '枚数': latest_balances[latest_balances['sub_type']=='airdrop']['balance'].iloc[0].round(0)
    },
        {
        '名前': '出金ウォレット',
        '枚数': latest_balances[latest_balances['sub_type']=='withdrawal']['balance'].iloc[0].round(0)
    },
    {
        '名前': 'Geekショップ用ウォレット',
        '枚数': latest_balances[latest_balances['sub_type']=='geek_shop']['balance'].iloc[0].round(0)
    },
    {
        '名前': 'ユーザー',
        '枚数': latest_balances[latest_balances['main_type']=='game_wallet']['balance'].sum().round(0)
    },
    {
        '名前': '取引所',
        '枚数': latest_balances[latest_balances['main_type']=='exchange']['balance'].sum().round(0)
    },
    {
        '名前': 'その他',
        '枚数': latest_balances[(latest_balances['main_type']=='others')&(latest_balances['sub_type']!='burn')]['balance'].sum().round(0)
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



