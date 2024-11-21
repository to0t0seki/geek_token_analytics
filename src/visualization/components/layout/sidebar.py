import streamlit as st
from datetime import datetime, timedelta
from src.data_access.database import get_latest_timestamp, db_file

def show_sidebar():
    latest_timestamp = get_latest_timestamp(db_file)
    latest_timestamp = (datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00')) + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')

    st.sidebar.markdown(f"""
    ### 説明
    最終更新：{latest_timestamp}JST\n
    日付の区切りは04:00JST\n
    一時間毎の更新
    """)
    
    st.sidebar.markdown("""
    ### 注意事項
    当ウェブサイトで提供されるトークンのホルダー分布や使用状況に関する情報は、ブロックチェーンのトランザクションAPIから取得したデータに基づいています。しかし、技術的な制約やAPIの更新頻度などにより、表示される情報が常に正確であるとは限りません。
    """)

    st.sidebar.markdown(f"""
    何か要望があればDiscordもしくは[X](https://twitter.com/tseki_is)で言ってください。
    """)