import streamlit as st
from src.database.data_access.queries import get_withdrawal_ranking, get_withdrawal_transactions
from src.visualization.components.sidebar import show_sidebar
from st_aggrid import AgGrid, GridUpdateMode
from src.database.data_access.database_client import DatabaseClient
import base64


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

style = '''
<style>
.stApp {
    background-image: url('https://lastmemories.io/special/assets/fankit-assets/PC/01_1_azumi.jpg');
    background-size: cover;
    background-repeat: no-repeat;
    }
.stCustomComponentV1 {
       max-width: 70% !important;
    }

</style>
'''
st.markdown(style, unsafe_allow_html=True)



st.title("出金アリーナランキング(1/11 04:00:00JST～)")

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

with st.spinner('データを取得中...'):
    withdrawal_df = get_withdrawal_ranking(st.session_state.db_client)
    withdrawal_transactions_df = get_withdrawal_transactions(st.session_state.db_client)


st.subheader('クリア回数(成功回数)ランキング')
withdrawal_df_count_sorted = withdrawal_df.sort_values(by='count', ascending=False)
withdrawal_df_count_sorted['rank'] = range(1, len(withdrawal_df_count_sorted) + 1)
withdrawal_df_count_sorted = withdrawal_df_count_sorted[['rank','to_address','count','value']]
withdrawal_df_count_sorted.rename(columns={'rank':'ランク','to_address':'アドレス','count':'回数','value':'総枚数'}, inplace=True)


count_ranking_response = AgGrid(
    withdrawal_df_count_sorted,
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE,
    key='count_ranking',
)

st.write("--------------------------------")
st.subheader('最大与ダメ(出金枚数)ランキング')


withdrawal_transactions_df_sorted = withdrawal_transactions_df.sort_values(by='value', ascending=False)[['address','timestamp','value']]
withdrawal_transactions_df_sorted['timestamp'] = withdrawal_transactions_df_sorted['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
withdrawal_transactions_df_sorted['rank'] = range(1, len(withdrawal_transactions_df_sorted) + 1)
withdrawal_transactions_df_sorted = withdrawal_transactions_df_sorted[['rank','address','timestamp','value']]
withdrawal_transactions_df_sorted.rename(columns={'rank':'ランク','address':'アドレス','timestamp':'達成日時','value':'出金枚数'}, inplace=True)



max_ranking_response = AgGrid(
    withdrawal_transactions_df_sorted,
    height=300,
    width='80%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE,
    key='max_ranking',
)

st.write('--------------------------------')
st.subheader('出金総額ランキング')
withdrawal_df_total_sorted = withdrawal_df.sort_values(by='value', ascending=False)
withdrawal_df_total_sorted['rank'] = range(1, len(withdrawal_df_total_sorted) + 1)
withdrawal_df_total_sorted = withdrawal_df_total_sorted[['rank','to_address','value','count']]
withdrawal_df_total_sorted.rename(columns={'rank':'ランク','to_address':'アドレス','count':'回数','value':'総枚数'}, inplace=True)


total_ranking_response = AgGrid(
    withdrawal_df_total_sorted,
    height=300,
    width='80%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE,
    key='total_ranking',
)

total_withdrawal = int(withdrawal_df['value'].sum())
total_count = withdrawal_transactions_df['tx_hash'].count()
average_withdrawal = int(total_withdrawal / total_count)
middle_withdrawal = int(withdrawal_transactions_df['value'].median())
max_withdrawal = int(withdrawal_transactions_df['value'].max())
min_withdrawal = int(withdrawal_transactions_df['value'].min())

st.markdown(f'''
***総出金枚数: {total_withdrawal}***  
***総出金回数: {total_count}***  
***平均出金枚数: {average_withdrawal}***  
***中央値出金枚数: {middle_withdrawal}***
''', unsafe_allow_html=True)
