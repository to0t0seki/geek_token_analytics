from src.data_access.query import get_nft_sell_transactions
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
from src.visualization.components.chart import display_nft_sell_chart
import streamlit as st
from src.visualization.components.sidebar import show_sidebar
from src.data_access.database_client import DatabaseClient

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")





st.title('NFT購入個数分布')
st.write('11/25-11/28のNFTセールをGeekで購入した人の個数分布です。')
if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

show_sidebar()

with st.spinner('データを取得中...'):
    df = get_nft_sell_transactions(st.session_state.db_client, "0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62")
df['value'] = df['value'].round(0).astype(int)
groupby_address_df = df.groupby('from_address')['value'].sum()
groupby_value_df = groupby_address_df.value_counts().sort_index().reset_index()


## データクレンジング
groupby_value_df['value'] = groupby_value_df['value']
groupby_value_df = groupby_value_df.drop([0,2,4,24])
groupby_value_df.loc[[1,3,23],'count'] += 1

groupby_value_df['buy_count'] = (groupby_value_df['value'] / 12500).astype(int)
groupby_value_df.drop(columns=['value'],inplace=True)
groupby_value_df = groupby_value_df[['buy_count', 'count']]



groupby_value_df.rename(columns={'count':'ユニークアドレス数','buy_count':'購入個数'}, inplace=True)
gb = GridOptionsBuilder.from_dataframe(groupby_value_df)




grid_response = AgGrid(
    groupby_value_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
)

st.markdown(f"""
合計個数：{(groupby_value_df['購入個数'] * groupby_value_df['ユニークアドレス数']).sum()}
合計アドレス数: {groupby_value_df['ユニークアドレス数'].sum()}
""")

display_nft_sell_chart(
    groupby_value_df,
    title='棒グラフ',
    legend_name='購入数',
)
