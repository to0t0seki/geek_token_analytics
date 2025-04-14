import streamlit as st
from src.database.data_access.queries.queries import get_withdrawal_ranking_in_usdt_2, get_withdrawal_transactions_in_usdt_2
from src.visualization.components.content import initialize_page
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder


initialize_page()



st.markdown(
    """
    <h1>
        出金アリーナランキングUSDT
    </h1>
    <h5>
        2/15 04:00:00JST～
    </h5>
    <span>
       4:04:00～4:04:20<br>
       12:00:00～12:00:20<br>
       20:00:00～20:00:20<br>  
       間の出金量を集計しています。<br>
    </span>
    """,
    unsafe_allow_html=True
)


with st.spinner('データを取得中...'):
    withdrawal_df = get_withdrawal_ranking_in_usdt_2(st.session_state.db_client)
    withdrawal_transactions_df = get_withdrawal_transactions_in_usdt_2(st.session_state.db_client)


st.subheader('クリア回数ランキング')
withdrawal_df_count_sorted = withdrawal_df.sort_values(by='count', ascending=False)
withdrawal_df_count_sorted['rank'] = range(1, len(withdrawal_df_count_sorted) + 1)
withdrawal_df_count_sorted = withdrawal_df_count_sorted[['rank','to_address','count','value_usd']]
withdrawal_df_count_sorted.rename(columns={'rank':'ランク','to_address':'アドレス','count':'回数','value_usd':'出金総額'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(withdrawal_df_count_sorted)
gb.configure_column('アドレス', filter=True)

count_ranking_response = AgGrid(
    withdrawal_df_count_sorted,
    gridOptions=gb.build(),
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

gb = GridOptionsBuilder.from_dataframe(withdrawal_transactions_df_sorted)
gb.configure_column('アドレス', filter=True)

max_ranking_response = AgGrid(
    withdrawal_transactions_df_sorted,
    gridOptions=gb.build(),
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

gb = GridOptionsBuilder.from_dataframe(withdrawal_df_total_sorted)
gb.configure_column('アドレス', filter=True)

total_ranking_response = AgGrid(
    withdrawal_df_total_sorted,
    gridOptions=gb.build(),
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
