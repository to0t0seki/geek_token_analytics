import streamlit as st
from src.visualization.components.layout.sidebar import show_sidebar


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()
st.title("更新履歴")

st.markdown("""### 2024-12-12
更新内容  
・データ更新を毎時00分から毎時10分に変更しました。            
・ データベースのチューニングを行いました。  
・ 取得出来ていないデータがあったので追加しました。以前とデータが若干変わっています。  
・ 更新履歴のページを追加しました。  
・ サイドバーの「最新トランザクション」を「最終更新時間」に変更しました。  
・ 表を複数選択出来るように設定しました。  
・ 全ての数値を３桁区切りにしました。  
""")

