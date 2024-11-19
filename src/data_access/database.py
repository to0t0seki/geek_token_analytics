import sqlite3
import pandas as pd


db_file = "data/processed/geek_transfers.db"

def get_balances(db_file: str, query: str, params: tuple = ()) -> pd.DataFrame:
    """
    指定されたクエリを使用してデータベースから残高を取得し、
    データフレームに格納して返す汎用関数
    """
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    # 日付列をdatetime型に変換
    df['date'] = pd.to_datetime(df['date'])
    
    # アドレスと日付でインデックスを設定
    df = df.set_index(['address', 'date'])
    return df

def get_all_balances(db_file: str) -> pd.DataFrame:
    """
    daily_balancesテーブルから全てのアドレスの最新の残高を取得
    """
    query = """
    SELECT address, date, CAST(balance AS INTEGER) as balance
    FROM adjusted_daily_balances
    WHERE address NOT LIKE '0x0000000000000000000000000000000000000000'
    ORDER BY date, balance DESC
    """
    return get_balances(db_file, query)

def get_airdrop_recipient_balances(db_file: str) -> pd.DataFrame:
    """
    airdropテーブルにあるアドレスの全ての日付の残高を取得
    """
    query = """
    WITH airdrop_addresses AS (
        SELECT DISTINCT to_address as address
        FROM airdrops
    )
    SELECT db.address, db.date, CAST(db.balance AS INTEGER) as balance
    FROM adjusted_daily_balances db
    INNER JOIN airdrop_addresses aa ON db.address = aa.address
    ORDER BY db.address, db.date
    """
    return get_balances(db_file, query)

def get_exchange_balances(db_file: str) -> pd.DataFrame:
    """
    指定されたアドレスの全ての日付の残高を取得
    """
    addresses = [
        '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23',
        '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe'
    ]
    query = """
    SELECT address, date, CAST(balance AS INTEGER) as balance
    FROM adjusted_daily_balances
    WHERE address IN ({})
    ORDER BY address, date
    """.format(','.join(['?']*len(addresses)))
    return get_balances(db_file, query, tuple(addresses))

def get_total_airdrops(db_file: str) -> dict:
    """
    各アドレスのtotal airdropを計算する
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    query = """
    SELECT td.to_address, CAST(SUM(td.value) AS INTEGER) as total_airdrop
    FROM airdrops a
    JOIN transfer_details td ON a.transfer_detail_id = td.id
    GROUP BY td.to_address
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    conn.close()
    
    return {address: total for address, total in results}

def get_daily_airdrops(db_file: str) -> pd.DataFrame:
    """
    指定されたアドレスの日次エアドロップ量を取得する
    日付の区切りは5時間後ろにずらす（例:2023-05-01 05:00:00 までは前日の2023-04-30としてカウント）
    
    :param db_file: データベースファイルのパス
    :param address: 取得対象のアドレス
    :return: 日付とエアドロップ量のDataFrame
    """
    conn = sqlite3.connect(db_file)
    query = """
    SELECT 
        DATE(DATETIME(timestamp, '+5 hours')) as date,
        CAST(SUM(value) AS INTEGER) as value,
        COUNT(DISTINCT to_address) as to_address_count,
        CAST(SUM(value) AS FLOAT) / COUNT(DISTINCT to_address) as per_address
    FROM 
        airdrops
    WHERE
        DATE(DATETIME(timestamp, '+5 hours')) >= '2024-09-26'
    GROUP BY 
        DATE(DATETIME(timestamp, '+5 hours'))  
    ORDER BY 
        date desc
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    
    return df

def get_daily_xgeek_to_geek(db_file: str) -> pd.DataFrame:
    """
    xgeek_to_geekビューから日次の合計値を計算する
    日付の区切りは5時間後ろにずらす（例:2023-05-01 05:00:00 までは前日の2023-04-30としてカウント）
    
    :param db_file: データベースファイルのパス
    :return: 日付とxgeekToGeek量の合計値のDataFrame
    """
    conn = sqlite3.connect(db_file)
    query = """
    SELECT 
        DATE(DATETIME(timestamp, '+5 hours')) as date,
        CAST(SUM(value) AS INTEGER) as value,
        COUNT(DISTINCT from_address) as address_count,
        CAST(SUM(value) AS FLOAT) / COUNT(DISTINCT from_address) as per_address
    FROM 
        xgeek_to_geek
    WHERE
        DATE(DATETIME(timestamp, '+5 hours')) >= '2024-09-26'
    GROUP BY 
        DATE(DATETIME(timestamp, '+5 hours'))
    ORDER BY 
        date desc
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    return df

def get_daily_export_token(db_file: str) -> pd.DataFrame:
    """
    export_tokenビューから日次の合計値を計算する
    日付の区切りは5時間後ろにずらす（例:2023-05-01 05:00:00 までは前日の2023-04-30としてカウント）
    
    :param db_file: データベースファイルのパス
    :return: 日付とexportToken量の合計値のDataFrame
    """
    conn = sqlite3.connect(db_file)
    query = """
    SELECT 
        DATE(DATETIME(timestamp, '+5 hours')) as date,
        CAST(SUM(value) AS INTEGER) as value,
        COUNT(DISTINCT to_address) as address_count,
        CAST(SUM(value) AS FLOAT) / COUNT(DISTINCT to_address) as per_address
    FROM 
        export_token
    WHERE
        to_address != '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' and
        DATE(DATETIME(timestamp, '+5 hours')) >= '2024-09-26'
    GROUP BY 
        DATE(DATETIME(timestamp, '+5 hours'))
    ORDER BY 
        date desc
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    

    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    return df

def get_airdrop_recipient_latest_balances(db_file: str) -> pd.DataFrame:
    """
    エアドロップを一度でも受け取ったことがあるアドレスの最新残高を取得
    """
    conn = sqlite3.connect(db_file)
    query = """
    SELECT db.address, db.date, CAST(db.balance AS INTEGER) AS balance
    FROM daily_balances db
    INNER JOIN (
        SELECT DISTINCT to_address AS address
        FROM airdrops
    ) airdrop ON db.address = airdrop.address
    WHERE db.address NOT LIKE '0x0000000000000000000000000000000000000000'
    ORDER BY db.date DESC, db.balance DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def get_airdrop_recipient_daily_total_balances(db_file: str) -> pd.DataFrame:
    """
    エアドロップを一度でも受け取ったことがあるアドレスの
    日次合計残高を取得
    """
    conn = sqlite3.connect(db_file)
    query = """
    SELECT db.date, SUM(CAST(db.balance AS INTEGER)) AS total_balance
    FROM adjusted_daily_balances db
    INNER JOIN (
        SELECT DISTINCT to_address AS address
        FROM airdrops
    ) airdrop ON db.address = airdrop.address
    WHERE db.address NOT LIKE '0x0000000000000000000000000000000000000000' and
        db.date >= '2024-09-26'
    GROUP BY db.date
    ORDER BY db.date desc
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def get_latest_timestamp(db_file: str) -> str:
    """
    transactionsテーブルから最新のタイムスタンプを取得する
    
    :param db_file: データベースファイルのパス
    :return: 最新のタイムスタンプ（文字列形式）
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    query = """
    SELECT timestamp
    FROM transactions
    ORDER BY timestamp DESC
    LIMIT 1
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    conn.close()
    
    return result[0] if result else None




