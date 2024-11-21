import streamlit as st
from src.visualization.components.charts.chart import display_chart
from src.data_access.database import get_airdrop_recipient_daily_total_balances, get_latest_timestamp, db_file
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder
from src.visualization.components.layout.google_analytics import add_google_analytics

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

latest_timestamp = get_latest_timestamp(db_file)
latest_timestamp = (datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00')) + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')


st.sidebar.markdown(f"""
### 説明
最終更新：{latest_timestamp}JST\n
日付の区切りは04:00JST\n
一時間毎の更新
""")
st.sidebar.markdown("""
### 注意事項
当ウェブサイトで提供されるトークンのホルダー分布や使用状況に関する情報は、ブロックチェーンのトランザクションAPIから取得したデータに基づいています。しかし、技術的な制約やAPIの更新頻度などにより、表示される情報が常に正確であるとは限りません。
""")


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