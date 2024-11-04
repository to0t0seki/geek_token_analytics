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
st.write(f"最終更新：{latest_timestamp}")
st.sidebar.success("上から表示したいデータを選択してください。")
st.sidebar.markdown("""
日付の区切りは04:00JSTです。\n
例：\n
2024-10-01 04:00_JSTから\n
2024-10-02 04:00_JSTまでは\n
2024-10-01とカウント。
""")

st.title(f"エアドロップ")
st.write("GEEKトークンのエアドロップ日次推移を表示します(単位：枚)。")


# xgeekToGeek の日次チャートを作成と表示
st.write("日次エアドロップ量")
airdrops_df = get_daily_airdrops(db_file)
airdrops_df['per_address'] = airdrops_df['per_address'].round(0)


gb = GridOptionsBuilder.from_dataframe(airdrops_df)


grid_response = AgGrid(
    airdrops_df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    width='100%',
    theme='streamlit' ,
)


total_airdrops = airdrops_df['value'].sum()
st.write(f"総エアドロップ量: {total_airdrops:,.0f}")



airdrops_df.drop(airdrops_df.columns[2:4], axis=1, inplace=True)

display_chart(
    airdrops_df,
    title='Geekトークンエアドロップ量(単位：枚)',
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
