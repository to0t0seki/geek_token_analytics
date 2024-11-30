import streamlit as st
from src.visualization.components.charts.chart import display_chart
from src.data_access.query import get_airdrop_recipient_balances
from src.visualization.components.layout.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()


st.title("プレイヤー残高")
st.write("一度でもエアドロップを受け取ったことのあるアドレスの合計残高。")



daily_total_balances_df = get_airdrop_recipient_balances()
grouped_df = daily_total_balances_df.groupby(level=1).sum()
grouped_df = grouped_df[grouped_df.index > '2024-09-26']
grouped_df.sort_index(ascending=False,inplace=True)
grouped_df.reset_index(inplace=True)
grouped_df['date'] = grouped_df['date'].dt.strftime('%Y-%m-%d')


gb = GridOptionsBuilder.from_dataframe(grouped_df)

column_names = {
    'date': '日付',
    'balance': '合計枚数'
}



for col_name, jp_name in column_names.items():
    gb.configure_column(
        col_name,
        header_name=jp_name,
    )
grid_response = AgGrid(
    grouped_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
)


display_chart(
    grouped_df,
    title='折れ線グラフ',
    chart_type='line',
    legend_name='合計枚数',
)
