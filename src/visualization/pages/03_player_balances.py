import streamlit as st
from src.visualization.components.charts.chart import display_chart
from src.data_access.database import get_airdrop_recipient_daily_total_balances, db_file
from src.visualization.components.layout.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()


st.title("プレイヤー残高")
st.write("一度でもエアドロップを受け取ったことのあるアドレスの合計残高。")


daily_total_balances_df = get_airdrop_recipient_daily_total_balances(db_file)
daily_total_balances_df['total_balance'] = daily_total_balances_df['total_balance'].round(0)



gb = GridOptionsBuilder.from_dataframe(daily_total_balances_df)

column_names = {
    'date': '日付',
    'total_balance': '合計枚数'
}


gb.configure_column("date", valueFormatter="value ? new Date(value).toISOString().split('T')[0] : ''")

for col_name, jp_name in column_names.items():
    gb.configure_column(
        col_name,
        header_name=jp_name,
    )
grid_response = AgGrid(
    daily_total_balances_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
)


display_chart(
    daily_total_balances_df,
    # title='プレイヤー残高',
)

# st.markdown("""
# プレイヤー:一度でもエアドロップを受け取ったことのあるアドレス
# """)