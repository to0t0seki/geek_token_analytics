import streamlit as st
from datetime import timedelta
from src.data_access.query import get_latest_timestamp
def show_sidebar():
    latest_timestamp = get_latest_timestamp()
    latest_timestamp = (latest_timestamp + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
    st.sidebar.image("img/logo2.jpg", width=200)

    st.sidebar.markdown(f"""
    ### 説明
    こちらはGEEKVerseのみのデータになります。\n
    毎時10分更新\n
    毎日の更新は04:15JST\n
    日付の区切りは04:00JST\n
    取得した最新のTX：{latest_timestamp}JST\n
    テーブル上で右クリックからCSVダウンロード可能\n
    
    
    """)
    
    st.sidebar.markdown("""
    ### 注意事項
    当ウェブサイトで提供されるトークンのホルダー分布や使用状況に関する情報は、ブロックチェーンのトランザクションAPIから取得したデータに基づいています。しかし、技術的な制約やAPIの更新頻度などにより、表示される情報が常に正確であるとは限りません。
    """)

    st.sidebar.markdown(f"""
    データに不正確な部分、不適切な表現、その他ご意見、ご要望等あれば[X](https://x.com/oegowbh)までお願いします。
    """)