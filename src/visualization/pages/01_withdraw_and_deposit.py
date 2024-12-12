import streamlit as st
from src.visualization.components.charts.chart import display_chart1
from src.data_access.query import get_daily_deposits, get_daily_withdrawals
from src.visualization.components.layout.sidebar import show_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode



st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()


st.title("入出金")



st.write("### 入金")
deposits_df = get_daily_deposits()
deposits_df['per_address'] = deposits_df['per_address'].round(0)
deposits_df['value'] = deposits_df['value'].round(0)




deposits_df.rename(columns={'date':'日付','value':'入金枚数','address_count':'ユニークアドレス数','per_address':'平均'}, inplace=True)
gb = GridOptionsBuilder.from_dataframe(deposits_df)


grid_response = AgGrid(
    deposits_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.SELECTION_CHANGED
)

total_deposits = deposits_df['入金枚数'].sum()
st.write(f"総入金枚数: {total_deposits:,.0f}")

st.write("")

st.write("### 出金")
withdrawals_df = get_daily_withdrawals()
withdrawals_df['per_address'] = withdrawals_df['per_address'].round(0)
withdrawals_df['value'] = withdrawals_df['value'].round(0)

withdrawals_df.rename(columns={'date':'日付','value':'出金枚数','address_count':'ユニークアドレス数','per_address':'平均'}, inplace=True)

gb = GridOptionsBuilder.from_dataframe(withdrawals_df)


grid_response = AgGrid(
    withdrawals_df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
)


total_withdrawals = withdrawals_df['出金枚数'].sum()
st.write(f"総出金枚数: {total_withdrawals:,.0f}")


withdrawals_df.drop(withdrawals_df.columns[2:4], axis=1, inplace=True)
deposits_df.drop(deposits_df.columns[2:4], axis=1, inplace=True)

display_chart1(
    deposits_df,
    withdrawals_df,
)

