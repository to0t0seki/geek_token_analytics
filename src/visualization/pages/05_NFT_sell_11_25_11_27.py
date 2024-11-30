from src.data_access.query import get_NFT_sell_transactions
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
from src.visualization.components.charts.chart import display_nft_sell_chart
import streamlit as st

df = get_NFT_sell_transactions("0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62")
groupby_address_df = df.groupby('from_address')['value'].sum()
groupby_value_df = groupby_address_df.value_counts().sort_index().reset_index()


## データクレンジング
groupby_value_df['value'] = groupby_value_df['value'].astype(int)
groupby_value_df = groupby_value_df.drop([0,2,4,24])
groupby_value_df.loc[[1,3,23],'count'] += 1

groupby_value_df['buy_count'] = (groupby_value_df['value'] / 12500).astype(int)
groupby_value_df.drop(columns=['value'],inplace=True)
groupby_value_df = groupby_value_df[['buy_count', 'count']]
# groupby_value_df.sort_values(by='buy_count', ascending=False, inplace=True)


print(groupby_value_df)
gb = GridOptionsBuilder.from_dataframe(groupby_value_df)

column_names = {
    'count': '人数',
    'buy_count': '購入個数',
}

for col_name, jp_name in column_names.items():
    gb.configure_column(
        col_name,
        header_name=jp_name,
    )

st.title('NFT購入個数分布')
st.write('11/25-11/28のNFTセールをGeekで購入した方の購入数別データです。')

grid_response = AgGrid(
    groupby_value_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
)

st.markdown(f"""
合計個数：{(groupby_value_df['buy_count'] * groupby_value_df['count']).sum()}
合計人数: {groupby_value_df['count'].sum()}
""")

display_nft_sell_chart(
    groupby_value_df,
    title='棒グラフ',
    legend_name='購入数',
)
