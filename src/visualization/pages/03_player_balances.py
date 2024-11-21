import streamlit as st
from src.visualization.components.charts.chart import display_chart
from src.data_access.database import get_airdrop_recipient_daily_total_balances, get_latest_timestamp, db_file
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

latest_timestamp = get_latest_timestamp(db_file)
latest_timestamp = (datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00')) + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
# ヘッダーの表示
st.write(f"最終更新：{latest_timestamp}JST(1時間毎更新)")
# st.sidebar.success("上から表示したいデータを選択してください。")
st.sidebar.markdown("""
日付の区切りは04:00JSTです。\n
""")


st.title("プレイヤー残高")
st.write("一度でもエアドロップを受け取ったことのあるアドレスの残高の合計。")


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
    update_mode=GridUpdateMode.SELECTION_CHANGED,
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