import streamlit as st
from src.visualization.components.charts.chart import display_chart1
from src.data_access.database import get_daily_xgeek_to_geek, get_daily_export_token, db_file
from src.visualization.components.layout.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()


st.title("入出金")



st.write("### 入金")
xgeek_to_geek_df = get_daily_xgeek_to_geek(db_file)
xgeek_to_geek_df['per_address'] = xgeek_to_geek_df['per_address'].round(0)


column_names = {
    'date': '日付',
    'value': '入金枚数',
    'address_count': 'アドレス数',
    'per_address': '平均'
}

gb = GridOptionsBuilder.from_dataframe(xgeek_to_geek_df)

for col_name, jp_name in column_names.items():
    gb.configure_column(
        col_name,
        header_name=jp_name,
        # 必要に応じて追加の設定
        # type=['numericColumn', 'numberColumnFilter'] など
    )


grid_response = AgGrid(
    xgeek_to_geek_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
)

total_xgeek_to_geek = xgeek_to_geek_df['value'].sum()
st.write(f"総入金枚数: {total_xgeek_to_geek:,.0f}")

st.write("")

st.write("### 出金")
export_token_df = get_daily_export_token(db_file)
export_token_df['per_address'] = export_token_df['per_address'].round(0)

column_names = {
    'date': '日付',
    'value': '出金枚数',
    'address_count': 'アドレス数',
    'per_address': '平均'
}
gb = GridOptionsBuilder.from_dataframe(export_token_df)

for col_name, jp_name in column_names.items():
    gb.configure_column(
        col_name,
        header_name=jp_name,
    )

grid_response = AgGrid(
    export_token_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
)


total_export_token = export_token_df['value'].sum()
st.write(f"総出金枚数: {total_export_token:,.0f}")


export_token_df.drop(export_token_df.columns[2:4], axis=1, inplace=True)
xgeek_to_geek_df.drop(xgeek_to_geek_df.columns[2:4], axis=1, inplace=True)

display_chart1(
    xgeek_to_geek_df,
    export_token_df,
    # title='Geekトークン入出金枚数',
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
