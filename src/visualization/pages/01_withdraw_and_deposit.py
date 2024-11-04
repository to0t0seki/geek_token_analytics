import streamlit as st
from src.visualization.components.charts.chart import display_chart1
from src.data_access.database import get_daily_xgeek_to_geek, get_daily_export_token, get_latest_timestamp, db_file
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


st.title("入出金")
st.write("GEEKトークンの入出金日次推移を表示します(単位：枚)。")


st.write("### 入金")
xgeek_to_geek_df = get_daily_xgeek_to_geek(db_file)
xgeek_to_geek_df['per_address'] = xgeek_to_geek_df['per_address'].round(0)



gb = GridOptionsBuilder.from_dataframe(xgeek_to_geek_df)


grid_response = AgGrid(
    xgeek_to_geek_df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    width='100%',
    theme='streamlit' ,
)

total_xgeek_to_geek = xgeek_to_geek_df['value'].sum()
st.write(f"総入金量: {total_xgeek_to_geek:,.0f}")

st.write("")

st.write("### 出金")
export_token_df = get_daily_export_token(db_file)
export_token_df['per_address'] = export_token_df['per_address'].round(0)

gb = GridOptionsBuilder.from_dataframe(export_token_df)


grid_response = AgGrid(
    export_token_df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    width='100%',
    theme='streamlit' ,
)


total_export_token = export_token_df['value'].sum()
st.write(f"総出金量: {total_export_token:,.0f}")


export_token_df.drop(export_token_df.columns[2:4], axis=1, inplace=True)
xgeek_to_geek_df.drop(xgeek_to_geek_df.columns[2:4], axis=1, inplace=True)

display_chart1(
    xgeek_to_geek_df,
    export_token_df,
    title='Geekトークン入出金量(単位：枚)',
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
