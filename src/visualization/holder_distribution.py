import streamlit as st
import plotly.express as px
import json
from src.data_access.database import get_all_balances, db_file, get_total_airdrops
from src.data_analysis.balance_calculations import get_latest_balances
from src.visualization.components.layout.sidebar import show_sidebar
import streamlit.components.v1 as components



st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")
rum_script = """
<script>
  (function(n,i,v,r,s,c,x,z){x=window.AwsRumClient={q:[],n:n,i:i,v:v,r:r,c:c};window[n]=function(c,p){x.q.push({c:c,p:p});};z=document.createElement('script');z.async=true;z.src=s;document.head.insertBefore(z,document.head.getElementsByTagName('script')[0]);})(
    'cwr',
    '3863a4ec-23f3-4a82-9e6d-9e950576a441',
    '1.0.0',
    'ap-northeast-1',
    'https://client.rum.us-east-1.amazonaws.com/1.19.0/cwr.js',
    {
      sessionSampleRate: 1,
      identityPoolId: "ap-northeast-1:d787bb61-c44f-4784-a78e-7fd6374048a3",
      endpoint: "https://dataplane.rum.ap-northeast-1.amazonaws.com",
      telemetries: ["performance","errors","http"],
      allowCookies: true,
      enableXRay: false
    }
  );
</script>
"""

components.html(rum_script, height=0)
show_sidebar()


st.title(f"ホルダー分布")


# st.write(f"現在のホルダー分布。")

# address.json を読み込む
with open("config/address.json", 'r') as f:
    address_data = json.load(f)

# カテゴリ名の日本語マッピングを定義
category_mapping = {
    'Game_Ops': 'ゲーム運営',
    'Airdrop Recipient': 'プレイヤー',
    'Exchange': '取引所',
    'Other': 'その他'
}

# アドレスの属性を定義する関数を修正
def categorize_address(address):
    if address in address_data:
        return category_mapping.get(address_data[address]['category'], address_data[address]['category'])
    elif total_airdrops.get(address, 0) > 0:
        return category_mapping['Airdrop Recipient']
    else:
        return category_mapping['Other']

# データの取得と処理
df = get_all_balances(db_file)
latest_balances = get_latest_balances(df)
total_airdrops = get_total_airdrops(db_file)


    


# アドレスを分類
latest_balances['カテゴリー'] = latest_balances['address'].apply(categorize_address)

# カテゴリごとの合計残高を計算
category_totals = latest_balances.groupby('カテゴリー')['balance'].sum().reset_index()
category_totals = category_totals.rename(columns={'balance': '枚数'})

# 円グラフの作成
fig = px.pie(
    category_totals,
    values='枚数', 
    names='カテゴリー', 
    # title='GEEKトークン保有者分布'
    )
fig.update_traces(textposition='inside', textinfo='percent+label')


# グラフの表示
st.plotly_chart(fig, use_container_width=True)

# 総供給量の計算と表示
total_supply = latest_balances['balance'].sum()
st.write(f"現在の総供給量: {total_supply:,.0f}")


st.markdown("""
###### ホルダーの説明

- ゲーム運営
    - airdrop用:0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7
    - 出金用:0x687F3413C7f0e089786546BedF809b8F8885B051
    - 運営ウォレット:0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62
- プレイヤー:エアドロップを一度でも受け取った事のあるアドレス
- 取引所
    - Bitget:0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23(Bitget)
    - Gate.io:0x0D0707963952f2fBA59dD06f2b425ace40b492Fe(Gate.io)
- その他:上記以外のウォレット
""")