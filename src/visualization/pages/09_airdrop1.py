import streamlit as st
import sys
import traceback
from src.data_access.client_1 import DatabaseClient
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def safe_exit_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.code(traceback.format_exc())
            # エラーを表示するだけで終了しない
            return None
    return wrapper

@safe_exit_handler
def get_daily_airdrops():
    query = """
    SELECT 
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) as date,
        SUM(value / 1000000000000000000.0) as value,
        COUNT(DISTINCT to_address) as to_address_count,
        SUM(value / 1000000000000000000.0) / COUNT(DISTINCT to_address) as per_address
    FROM 
        airdrops
    WHERE
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) >= '2024-09-26'
    GROUP BY 
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR))  
    ORDER BY 
        date desc
    """
    client = DatabaseClient()
    df = client.query_to_df(query)
    
    
    return df

def main():
    try:
        st.set_page_config(page_title="Airdrop Analysis", layout="wide")
        
        # データベース接続をセッションステートで管理
        if 'db_client' not in st.session_state:
            st.session_state.db_client = DatabaseClient()
        
        # 処理の実行
        with st.spinner('データを取得中...'):
            df = get_daily_airdrops()
            
        if df is not None and not df.empty:
            st.write(df)
        else:
            st.warning("データを取得できませんでした")
            
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {str(e)}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()