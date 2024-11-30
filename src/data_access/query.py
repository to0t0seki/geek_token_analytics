import pandas as pd
from src.data_access.client import DatabaseClient




def get_all_balances() -> pd.DataFrame:
    """
    daily_balancesテーブルから全てのアドレスの全ての日付の残高を取得
    """
    query = """
    SELECT address, date, CAST(balance AS INTEGER) as balance
    FROM adjusted_daily_balances
    WHERE address NOT LIKE '0x0000000000000000000000000000000000000000'
    ORDER BY date, balance DESC
    """
    client = DatabaseClient()
    df = client.query_to_df_with_address_date_index(query)

    return df


def get_airdrop_recipient_balances() -> pd.DataFrame:
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
    """
    client = DatabaseClient()
    df = client.query_to_df_with_address_date_index(query)
   
    return df


def get_exchange_balances() -> pd.DataFrame:
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

    client = DatabaseClient()
    df = client.query_to_df_with_address_date_index(query, params=tuple(addresses))

    return df

# def get_total_airdrops() -> dict:
#     """
#     各アドレスのtotal airdropを計算する
#     """
#     db_file = 'data/processed/geek_transfers.db'
    
    
#     query = """
#     SELECT to_address, CAST(SUM(value) AS INTEGER) as total_airdrop
#     FROM airdrops
#     GROUP BY to_address
#     """

    
#     conn = sqlite3.connect(db_file)
#     cursor = conn.cursor()

#     cursor.execute(query)
#     results = cursor.fetchall()
    
#     conn.close()
    
#     return {address: total for address, total in results}


def get_daily_airdrops() -> pd.DataFrame:
    """
    指定されたアドレスの日次エアドロップ量を取得する
    日付の区切りは5時間後ろにずらす（例:2023-05-01 05:00:00 までは前日の2023-04-30としてカウント）
    
    :param db_file: データベースファイルのパス
    :param address: 取得対象のアドレス
    :return: 日付とエアドロップ量のDataFrame
    """
    
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
    client = DatabaseClient()
    df = client.query_to_df(query)
    
    
    return df


def get_daily_xgeek_to_geek() -> pd.DataFrame:
    """
    日付毎の出金枚数を取得
    日付の区切りは5時間後ろにずらす（例:2023-05-01 05:00:00 までは前日の2023-04-30としてカウント）
    """
    
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
    client = DatabaseClient()
    df = client.query_to_df(query)

    
    return df



def get_daily_export_token() -> pd.DataFrame:
    """
    export_tokenビューから日次の合計値を計算する
    日付の区切りは5時間後ろにずらす（例:2023-05-01 05:00:00 までは前日の2023-04-30としてカウント）
    
    :param db_file: データベースファイルのパス
    :return: 日付とexportToken量の合計値のDataFrame
    """
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
    
    client = DatabaseClient()
    df = client.query_to_df(query)
    
    return df


def get_latest_timestamp() -> str:
    """
    transactionsテーブルから最新のタイムスタンプを取得する
    
    :param db_file: データベースファイルのパス
    :return: 最新のタイムスタンプ（文字列形式）
    """

    
    query = """
    SELECT max(timestamp)
    FROM transactions
    """
    
    client = DatabaseClient()
    result = client.fetch_one(query)
    
    return result[0]



def get_latest_balances_from_all_addresses() -> pd.DataFrame:
    """
    全てのアドレスの最新の残高を取得
    """
    query = """
    SELECT
        t1.date,
        t1.address,
        t1.balance
    FROM adjusted_daily_balances t1
    INNER JOIN (
        SELECT address, MAX(date) as max_date
        FROM adjusted_daily_balances
        GROUP BY address
        ) t2 ON t1.address = t2.address 
        AND t1.date = t2.max_date
    WHERE t1.address != '0x0000000000000000000000000000000000000000'
    ORDER BY t1.balance DESC
    """
    client = DatabaseClient()
    df = client.query_to_df(query)
    return df

def get_latest_balances_from_airdrop_recipient() -> pd.DataFrame:
    """
    エアドロップを一度でも受け取ったことがあるアドレスの最新の残高を取得
    """
    query = """
    WITH latest_balances AS (
        SELECT
            t1.date,
            t1.address,
            t1.balance
        FROM adjusted_daily_balances t1
        INNER JOIN (
            SELECT address, MAX(date) as max_date
            FROM adjusted_daily_balances
            GROUP BY address
        ) t2 ON t1.address = t2.address 
            AND t1.date = t2.max_date
    )
    SELECT lb.address, lb.date, lb.balance
    FROM latest_balances as lb
    INNER JOIN (
        SELECT DISTINCT to_address as address
        FROM airdrops
    ) as apd ON lb.address = apd.address
    """
    client = DatabaseClient()
    df = client.query_to_df(query)
    return df



def get_latest_balances_from_exchange() -> pd.DataFrame:
    """
    エクスチェンジアドレスの最新の残高を取得
    """
    addresses = [
        '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23',
        '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe'
    ]
    query = """
    WITH latest_balances AS (
        SELECT
            t1.date,
        t1.address,
        t1.balance
    FROM adjusted_daily_balances t1
    INNER JOIN (
        SELECT address, MAX(date) as max_date
        FROM adjusted_daily_balances
        GROUP BY address
        ) t2 ON t1.address = t2.address 
        AND t1.date = t2.max_date
    )
    SELECT lb.address, lb.date, lb.balance
    FROM latest_balances as lb
    INNER JOIN (
        SELECT ? as address
        UNION ALL
        SELECT ?
    ) as exd ON lb.address = exd.address
    """
    client = DatabaseClient()
    df = client.query_to_df(query, params=tuple(addresses))
    return df

def get_latest_balances_from_operator() -> pd.DataFrame:
    """
    運営アドレスの最新の残高を取得
    """
    addresses = [
        '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7',  # Airdrop_Wallet
        '0x687F3413C7f0e089786546BedF809b8F8885B051',  # Xgeek_Withdrawal_Wallet
        '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62'   # Game_Ops_Wallet
    ]
    query = """
    WITH latest_balances AS (
        SELECT
            t1.date,
            t1.address,
            t1.balance
        FROM adjusted_daily_balances t1
        INNER JOIN (
            SELECT address, MAX(date) as max_date
            FROM adjusted_daily_balances
            GROUP BY address
        ) t2 ON t1.address = t2.address 
            AND t1.date = t2.max_date
    )
    SELECT lb.address, lb.date, lb.balance
    FROM latest_balances as lb
    INNER JOIN (
        SELECT ? as address
        UNION ALL
        SELECT ?
        UNION ALL
        SELECT ?
    ) as op ON lb.address = op.address
    """
    client = DatabaseClient()
    df = client.query_to_df(query, params=tuple(addresses))
    return df

def get_latest_balances_from_game_ops_wallet() -> pd.DataFrame:
    query = """
    SELECT balance
    FROM adjusted_daily_balances
    where address = '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62'
    ORDER BY date DESC
    LIMIT 1
    """
    client = DatabaseClient()
    df = client.query_to_df(query)
    return df

def get_latest_balances_from_withdrawal_wallet() -> pd.DataFrame:
    query = """
    SELECT balance
    FROM adjusted_daily_balances
    where address = '0x687F3413C7f0e089786546BedF809b8F8885B051'
    ORDER BY date DESC
    LIMIT 1
    """
    client = DatabaseClient()
    df = client.query_to_df(query)
    return df

def get_latest_balances_from_airdrop_wallet() -> pd.DataFrame:
    query = """
    SELECT balance
    FROM adjusted_daily_balances
    where address = '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7'
    ORDER BY date DESC
    LIMIT 1
    """
    client = DatabaseClient()
    df = client.query_to_df(query)
    return df

def get_latest_balances_from_others() -> pd.DataFrame:
    """
    運営、取引所、エアドロップ受領者以外のアドレスの最新残高を取得
    
    除外アドレス：
    - 運営アドレス (Game_Ops_Wallet, Airdrop_Wallet, Xgeek_Withdrawal_Wallet)
    - 取引所アドレス (0x1AB4973a..., 0x0D070796...)
    - エアドロップ受領者
    """
    operator_addresses = [
        '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7',  # Airdrop_Wallet
        '0x687F3413C7f0e089786546BedF809b8F8885B051',  # Xgeek_Withdrawal_Wallet
        '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62'   # Game_Ops_Wallet
    ]
    
    exchange_addresses = [
        '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23',
        '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe'
    ]
    
    query = """
    WITH latest_balances AS (
        SELECT
            t1.date,
            t1.address,
            t1.balance
        FROM adjusted_daily_balances t1
        INNER JOIN (
            SELECT address, MAX(date) as max_date
            FROM adjusted_daily_balances
            GROUP BY address
        ) t2 ON t1.address = t2.address 
            AND t1.date = t2.max_date
    ),
    excluded_addresses AS (
        SELECT ? as address
        UNION ALL SELECT ?
        UNION ALL SELECT ?
        UNION ALL SELECT ?
        UNION ALL SELECT ?
        UNION ALL SELECT "0x0000000000000000000000000000000000000000"
        UNION ALL
        SELECT DISTINCT to_address as address
        FROM airdrops
    )
    SELECT lb.address, lb.date, lb.balance
    FROM latest_balances lb
    LEFT JOIN excluded_addresses ea ON lb.address = ea.address
    WHERE ea.address IS NULL
    """
    
    client = DatabaseClient()
    df = client.query_to_df(query, params=tuple(operator_addresses + exchange_addresses))
    return df

def get_address_info(address: str) -> pd.DataFrame:
    """
    指定されたアドレスの情報を取得
    """
    query = """
    WITH balances AS (
        SELECT date, balance as balance
        FROM adjusted_daily_balances
        WHERE address = ? and date >= '2024-09-26'
    ),
    airdrop as (
        SELECT 
            DATE(DATETIME(timestamp, '+5 hours')) as date,
            SUM(value) as airdrop
        FROM airdrops
        WHERE 
            to_address = ? and 
            DATE(DATETIME(timestamp, '+5 hours')) >= '2024-09-26'
        GROUP BY DATE(DATETIME(timestamp, '+5 hours'))
    ),
    withdraw as (   
        SELECT 
            DATE(DATETIME(timestamp, '+5 hours')) as date,
            SUM(value) as withdraw
        FROM export_token
        WHERE 
            to_address = ? and
            DATE(DATETIME(timestamp, '+5 hours')) >= '2024-09-26'
        GROUP BY DATE(DATETIME(timestamp, '+5 hours'))
    ),
    deposit as (
        SELECT 
            DATE(DATETIME(timestamp, '+5 hours')) as date,
            SUM(value) as deposit
        FROM xgeek_to_geek
        WHERE 
            from_address = ? and 
            DATE(DATETIME(timestamp, '+5 hours')) >= '2024-09-26'
        GROUP BY DATE(DATETIME(timestamp, '+5 hours'))
    )
    SELECT 
        b.date,
        b.balance,
        COALESCE(a.airdrop, 0) as airdrop,
        COALESCE(w.withdraw, 0) as withdraw,
        COALESCE(d.deposit, 0) as deposit
    FROM balances b
    LEFT JOIN airdrop a ON b.date = a.date
    LEFT JOIN withdraw w ON b.date = w.date
    LEFT JOIN deposit d ON b.date = d.date
    ORDER BY b.date DESC    
    """
    client = DatabaseClient()
    df = client.query_to_df(query, params=(address, address, address, address))
    return df


def get_NFT_sell_transactions(address:str)->pd.DataFrame:
    query = f"""
    SELECT * 
    FROM transactions t join transfer_details td on t.tx_hash = td.tx_hash
    WHERE td.to_address = '{address}' and
    t.timestamp between '2024-11-25T10:00:00.000000Z' and '2024-11-27T15:00:00.000000Z' and 
    td.method = 'transfer'
    """
    client = DatabaseClient()
    df = client.query_to_df(query)
    return df



# df = get_least_balances_from_all_addresses()
# print(df['balance'].sum())
# df = get_latest_balances_from_airdrop_recipient()
# print(df['balance'].sum())
# df = get_latest_balances_from_exchange()
# print(df['balance'].sum())
# df = get_latest_balances_from_others()
# print(df['balance'].sum())

