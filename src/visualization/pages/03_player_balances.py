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
st.write(f"最終更新：{latest_timestamp}")
st.sidebar.success("上から表示したいデータを選択してください。")
st.sidebar.markdown("""
日付の区切りは04:00JSTです。\n
例：\n
2024-10-01 04:00_JSTから\n
2024-10-02 04:00_JSTまでは\n
2024-10-01とカウント。
""")


st.title("プレイヤー残高")
st.write("プレイヤーのトータル残高日次推移を表示します(単位：枚)。")


daily_total_balances_df = get_airdrop_recipient_daily_total_balances(db_file)
daily_total_balances_df['total_balance'] = daily_total_balances_df['total_balance'].round(0)



gb = GridOptionsBuilder.from_dataframe(daily_total_balances_df)
gb.configure_column("date", valueFormatter="value ? new Date(value).toISOString().split('T')[0] : ''")


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
    title='プレイヤー残高(単位：枚)',
)

st.markdown("""
プレイヤーの定義:一度でもエアドロップを受け取ったことのあるアドレス
""")