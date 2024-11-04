import pandas as pd
from src.data_access.database import db_file, get_total_airdrops
import json
# address.json を読み込む
with open('config/address.json', 'r') as f:
    address_data = json.load(f)


def get_latest_balances(df: pd.DataFrame) -> pd.DataFrame:
    """
    全ての日付の残高を含むデータフレームから、
    各アドレスの最新の残高のみを抽出したデータフレームを作成する
    
    :param df: get_current_balances() または get_airdrop_recipient_balances() で取得したデータフレーム
    :return: 最新の残高のみを含むデータフレーム（日付列なし）
    """
    # 各アドレスの最新の残高を取得
    latest_balances = df.groupby(level='address')['balance'].last().reset_index()

    # total_airdrop を計算して追加
    total_airdrops = get_total_airdrops(db_file)
    latest_balances['total_airdrop'] = latest_balances['address'].map(total_airdrops).fillna(0)

    # Note 列を追加
    latest_balances['Note'] = latest_balances['address'].map(lambda x: address_data.get(x, {}).get('name', ''))

    
    
    
    # 残高でソート
    latest_balances = latest_balances.sort_values('balance', ascending=False)
    
    return latest_balances

def calculate_daily_total_balance(df: pd.DataFrame) -> pd.DataFrame:
    """
    全アドレスの残高データから、日付ごとの合計残高を計算する

    :param df: get_latest_balances() の返り値のデータフレーム
    :return: 日付ごとの合計残高を含むデータフレーム
    """
    # 日付でグループ化し、残高の合計を計算
    daily_total = df.groupby('date')['balance'].sum().reset_index()
    
    # 日付でソート
    daily_total = daily_total.sort_values('date')
    
    # 日付をインデックスに設定
    daily_total = daily_total.set_index('date')
    
    return daily_total