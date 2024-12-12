import streamlit as st
from src.visualization.components.layout.sidebar import show_sidebar


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()
st.title("変更履歴")

st.markdown("""### 2024-12-10
更新内容    
* 全てのページの計算方法を修正しました。若干以前と数値が変わっています。
* 更新履歴のページを追加しました。
""")

