import streamlit as st
from src.database.data_access.queries import get_withdrawal_ranking_in_usdt_1, get_withdrawal_transactions_in_usdt_1
from src.visualization.components.sidebar import show_sidebar
from st_aggrid import AgGrid, GridUpdateMode
from src.database.data_access.database_client import DatabaseClient


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
       max-width: 90% !important;
    }

</style>
'''
st.markdown(style, unsafe_allow_html=True)



st.markdown(
    """
    <h1>
        出金アリーナランキング(<span style="color:red;">ドル建て</span>
    </h1>
    <h5>
        1/11 04:00:00JST～2/15 04:00:00JST
    </h5>
    <span>
       4:04:00～4:04:20<br>
       12:00:00～12:00:20<br>
       20:00:00～20:00:20<br>  
       の間のexportTokenメソッドのトランザクション(出金トランザクション)を<br>
       取得し集計＆表示しています。<br>
    </span>
    """,
    unsafe_allow_html=True
)

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

with st.spinner('データを取得中...'):
    withdrawal_df = get_withdrawal_ranking_in_usdt_1(st.session_state.db_client)
    withdrawal_transactions_df = get_withdrawal_transactions_in_usdt_1(st.session_state.db_client)


st.subheader('クリア回数ランキング')
withdrawal_df_count_sorted = withdrawal_df.sort_values(by='count', ascending=False)
withdrawal_df_count_sorted['rank'] = range(1, len(withdrawal_df_count_sorted) + 1)
withdrawal_df_count_sorted = withdrawal_df_count_sorted[['rank','to_address','count','value_usd']]
withdrawal_df_count_sorted.rename(columns={'rank':'ランク','to_address':'アドレス','count':'回数','value_usd':'出金総額'}, inplace=True)


count_ranking_response = AgGrid(
    withdrawal_df_count_sorted,
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE,
    key='count_ranking',
)

st.write("--------------------------------")
st.subheader('最大与ダメランキング')


withdrawal_transactions_df_sorted = withdrawal_transactions_df.sort_values(by='value_usd', ascending=False)
withdrawal_transactions_df_sorted['timestamp'] = withdrawal_transactions_df_sorted['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
withdrawal_transactions_df_sorted['rank'] = range(1, len(withdrawal_transactions_df_sorted) + 1)
withdrawal_transactions_df_sorted = withdrawal_transactions_df_sorted[['rank','address','timestamp','value_usd','value','close']]
withdrawal_transactions_df_sorted.rename(columns={'rank':'ランク','address':'アドレス','timestamp':'達成日時','value':'出金枚数','close':'geek価格','value_usd':'出金額'}, inplace=True)



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
withdrawal_df_total_sorted = withdrawal_df.sort_values(by='value_usd', ascending=False)
withdrawal_df_total_sorted['rank'] = range(1, len(withdrawal_df_total_sorted) + 1)
withdrawal_df_total_sorted = withdrawal_df_total_sorted[['rank','to_address','value_usd','count']]
withdrawal_df_total_sorted.rename(columns={'rank':'ランク','to_address':'アドレス','count':'回数','value_usd':'出金総額'}, inplace=True)


total_ranking_response = AgGrid(
    withdrawal_df_total_sorted,
    height=300,
    width='80%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE,
    key='total_ranking',
)

total_withdrawal = int(withdrawal_df['value_usd'].sum())
total_count = withdrawal_transactions_df['tx_hash'].count()
average_withdrawal = int(total_withdrawal / total_count)
middle_withdrawal = int(withdrawal_transactions_df['value_usd'].median())
max_withdrawal = int(withdrawal_transactions_df['value_usd'].max())
min_withdrawal = int(withdrawal_transactions_df['value'].min())

st.markdown(f'''
<div style="background-color: white; width: 200px;">
総出金額: {total_withdrawal}<br>
総出金回数: {total_count}<br>
平均出金額: {average_withdrawal}<br>
中央値出金額: {middle_withdrawal}<br>
</div>
''', unsafe_allow_html=True)
