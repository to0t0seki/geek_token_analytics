import mysql.connector
import pandas as pd
import streamlit as st
import sys
import traceback

class DatabaseClient:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'taka4586',
            'port': 3306,
            'database': 'geek_database',
            'connection_timeout': 30,
            'raise_on_warnings': True
        }
        self._connection = None

    def get_connection(self):
        try:
            if self._connection is None or not self._connection.is_connected():
                self._connection = mysql.connector.connect(**self.config)
            return self._connection
        except mysql.connector.Error as e:
            st.error(f"データベース接続エラー: {str(e)}")
            st.code(traceback.format_exc())
            # エラーを表示するだけで終了しない
            return None

    def query_to_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        try:
            conn = self.get_connection()
            if conn is None:
                return pd.DataFrame()
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
            
        except Exception as e:
            st.error(f"クエリ実行エラー: {str(e)}")
            st.code(traceback.format_exc())
            return pd.DataFrame()
        
        finally:
            try:
                if self._connection is not None and self._connection.is_connected():
                    self._connection.close()
                    self._connection = None
            except Exception:
                pass