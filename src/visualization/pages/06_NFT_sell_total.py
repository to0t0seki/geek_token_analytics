import streamlit as st
from src.visualization.components.layout.sidebar import show_sidebar
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
from src.visualization.components.charts.chart import display_nft_sell_chart
from src.data_access.query import get_nft_transactions
from src.data_access.client import DatabaseClient

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

st.title("NFTセール集計（11/12-11/27）")

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()

st.write(st.session_state.db_client)
show_sidebar()

with st.spinner('データを取得中...'):
    df = get_nft_transactions()
tmp = df.groupby('count').count().reset_index()
tmp.rename(columns={'count':'購入個数','to_address':'ユニークアドレス数'}, inplace=True)

total_count = tmp['購入個数'] * tmp['ユニークアドレス数']
total_people = tmp['ユニークアドレス数'].sum()




gb = GridOptionsBuilder.from_dataframe(tmp)


grid_response = AgGrid(
    tmp,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
)

st.write(f"合計個数：{total_count.sum()}")
st.write(f"合計アドレス数: {total_people}")

display_nft_sell_chart(
    tmp,
    title='棒グラフ',
    legend_name='購入数',
)

st.markdown("""
## 羽根つきの数について

結果からいう最低SSが12個、Sが43個ほど出回っていると思います。

理由は以下の通り：

- SSにおいては100以上購入したアドレスは11で、その内200以上購入したアドレスは1つ（192の方は多分ウォレット合算しているため）

- Sにおいては：
  - 50-99は18個
  - 100-149は9個
  - 150-199は1個
  - 200以上は1個
  
  よって、1×18 + 2×9 + 3×1 + 4×1 = 43個ほど

ただし合算しているアドレスもあるため、最低ラインです。
""")
