import streamlit as st
import plotly.express as px
import json
from src.data_access.database import get_all_balances, db_file, get_total_airdrops, get_latest_timestamp
from src.data_analysis.balance_calculations import get_latest_balances
from datetime import datetime, timedelta
import hashlib
import base64
from cryptography.fernet import Fernet
import hmac
import hashlib
import os
from src.data_collection.transfer_data_collector_db import run_update


# ENCRYPTION_KEY = os.getenv("ENCY")

def decrypt_key(encrypted_key):
    try:
        f = Fernet(ENCRYPTION_KEY)
        decrypted_key = f.decrypt(base64.urlsafe_b64decode(encrypted_key))
        return decrypted_key.decode()
    except Exception as e:
        st.error(f"キーの復号化に失敗しました: {e}")
        return None
    
def verify_key(provided_key):
    expected_hash = hmac.new(SECRET_KEY.encode(), msg=provided_key.encode(), digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_hash, provided_key)

def secure_function():
    st.write("認証成功！セキュアな関数が実行されました。")
    run_update()

st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

if st.query_params.get('api_key'):
    st.write("APIキーがあります。")
else:
    st.write("APIキーがありません")

encrypted_key = st.query_params.get("X-Encrypted-Key", [""])[0]

if encrypted_key:
    decrypted_key = decrypt_key(encrypted_key)
    if decrypted_key and verify_key(decrypted_key):
        secure_function()



latest_timestamp = get_latest_timestamp(db_file)
latest_timestamp = (datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00')) + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
# ヘッダーの表示
st.write(f"最終更新：{latest_timestamp} JST")
st.sidebar.success("上から表示したいデータを選択してください。")
st.sidebar.markdown("""
日付の区切りは04:00JSTです。\n
例：\n
2024-10-01 04:00_JSTから\n
2024-10-02 04:00_JSTまでは\n
2024-10-01とカウント。
""")
   


st.title(f"ホールド分布")


st.write(f"GEEKトークンの現在のホールド分布を表示します。")

# address.json を読み込む
with open("config/address.json", 'r') as f:
    address_data = json.load(f)

# データの取得と処理
df = get_all_balances(db_file)
latest_balances = get_latest_balances(df)
total_airdrops = get_total_airdrops(db_file)

# アドレスの属性を定義する関数
def categorize_address(address):
    if address in address_data:
        return address_data[address]['category']
    elif total_airdrops.get(address, 0) > 0:
        return 'Airdrop Recipient'
    else:
        return 'Other'
    


# アドレスを分類
latest_balances['Category'] = latest_balances['address'].apply(categorize_address)

# カテゴリごとの合計残高を計算
category_totals = latest_balances.groupby('Category')['balance'].sum().reset_index()

# 円グラフの作成
fig = px.pie(category_totals, values='balance', names='Category', title='GEEK Token Holder Distribution')
fig.update_traces(textposition='inside', textinfo='percent+label')

# グラフの表示
st.plotly_chart(fig, use_container_width=True)

# 総供給量の計算と表示
total_supply = latest_balances['balance'].sum()
st.write(f"Current Total Supply: {total_supply:,.0f}")


st.markdown("""
### ホールド分布の説明

- Game_Ops:ゲーム運営(把握している分)
    - 0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7(airdrop用)
    - 0x687F3413C7f0e089786546BedF809b8F8885B051(出金用)
    - 0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62
- Airdrop Recipient:エアドロップを一度でも受け取った事のあるアドレス
- Exchange: Bitget,Gate.io
    - 0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23
    - 0x0D0707963952f2fBA59dD06f2b425ace40b492Fe
- Other:その他
""")