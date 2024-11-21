import streamlit as st
from src.visualization.components.charts.chart import display_chart
from src.data_access.database import get_daily_airdrops, get_latest_timestamp, db_file
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

latest_timestamp = get_latest_timestamp(db_file)
latest_timestamp = (datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00')) + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
# ヘッダーの表示
st.write(f"最終更新：{latest_timestamp}JST(1時間毎更新)")
# st.sidebar.success("上から見たいデータを選んでください。")
st.sidebar.markdown("""
日付の区切りは04:00JSTです。\n
""")

st.title(f"エアドロップ")
st.write("エアドロップの日次推移。")


# xgeekToGeek の日次チャートを作成と表示
# st.write("日次エアドロップ"
airdrops_df = get_daily_airdrops(db_file)
airdrops_df['per_address'] = airdrops_df['per_address'].round(0)

column_names = {
    'date': '日付',
    'value': '枚数',
    'to_address_count': 'アドレス数（受け取った）',
    'per_address': '平均'
}

gb = GridOptionsBuilder.from_dataframe(airdrops_df)

for col_name, jp_name in column_names.items():
    gb.configure_column(
        col_name,
        header_name=jp_name,
        # 必要に応じて追加の設定
        # type=['numericColumn', 'numberColumnFilter'] など
    )


grid_response = AgGrid(
    airdrops_df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    width='100%',
    theme='streamlit' ,
)


total_airdrops = airdrops_df['value'].sum()
st.write(f"総エアドロップ枚数: {total_airdrops:,.0f}")



airdrops_df.drop(airdrops_df.columns[2:4], axis=1, inplace=True)

display_chart(
    airdrops_df,
    # title='Geekトークンエアドロップ枚数',
)

# export_token_csv = export_token_df.to_csv(encoding='utf-8')
# st.download_button(
#     label="出金データをCSVとしてダウンロード",
#     data=export_token_csv,
#     file_name='export_token_data.csv',
#     mime='text/csv',
# )

# xgeek_to_geek_csv = xgeek_to_geek_df.to_csv(encoding='utf-8')
# st.download_button(
#     label="入金データをCSVとしてダウンロード",
#     data=xgeek_to_geek_csv,
#     file_name='xgeek_to_geek_data.csv',
#     mime='text/csv',
# )
