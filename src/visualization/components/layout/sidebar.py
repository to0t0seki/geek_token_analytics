import streamlit as st
from datetime import datetime, timedelta
from src.data_access.query import get_latest_timestamp

def show_sidebar():
    latest_timestamp = get_latest_timestamp()
    latest_timestamp = (datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00')) + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')

    st.sidebar.markdown(f"""
    ### 説明
    毎時00分更新\n
    日付の区切りは04:00JST\n
    最新のトランザクション：{latest_timestamp}JST\n
    テーブル上で右クリックからCSVダウンロード可能\n
    
    
    """)
    
    st.sidebar.markdown("""
    ### 注意事項
    当ウェブサイトで提供されるトークンのホルダー分布や使用状況に関する情報は、ブロックチェーンのトランザクションAPIから取得したデータに基づいています。しかし、技術的な制約やAPIの更新頻度などにより、表示される情報が常に正確であるとは限りません。
    """)

    st.sidebar.markdown(f"""
    データに不正確な部分、不適切な表現、その他ご意見、ご要望等あれば[X](https://x.com/oegowbh)までお願いします。
    """)