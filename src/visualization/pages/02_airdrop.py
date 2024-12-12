import streamlit as st
from src.visualization.components.charts.chart import display_chart
from src.data_access.query import get_daily_airdrops
from src.visualization.components.layout.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()

st.title(f"エアドロップ")



# xgeekToGeek の日次チャートを作成と表示
# st.write("日次エアドロップ"
airdrops_df = get_daily_airdrops()
airdrops_df['per_address'] = airdrops_df['per_address'].round(0)
airdrops_df['value'] = airdrops_df['value'].round(0)

airdrops_df.rename(columns={'date':'日付','value':'枚数','to_address_count':'ユニークアドレス数','per_address':'平均'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(airdrops_df)
gb.configure_columns(
    ["枚数", "ユニークアドレス数", "平均"],
    valueFormatter="Math.floor(value).toLocaleString()"
)
gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)


grid_response = AgGrid(
    airdrops_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.NO_UPDATE,
)


total_airdrops = airdrops_df['枚数'].sum()
st.write(f"総エアドロップ枚数: {total_airdrops:,.0f}")



airdrops_df.drop(airdrops_df.columns[2:4], axis=1, inplace=True)

display_chart(
    airdrops_df,
    title='折れ線グラフ',
    chart_type='line',
    legend_name='エアドロップ',
)
