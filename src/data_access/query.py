import streamlit as st

def get_all_balances():
    """
    daily_balancesテーブルから全てのアドレスの全ての日付の残高を取得
    """
    query = """
    SELECT address, date, balance
    FROM adjusted_daily_balances
    WHERE address != '0x0000000000000000000000000000000000000000'
    ORDER BY date, balance DESC
    limit 10
    """
    df = st.session_state.db_client.query_to_df_with_address_date_index(query)

    return df


def get_airdrop_recipient_balances():
    """
    airdropsテーブルにあるアドレスの全ての日付の残高を取得
    """
    query = """
    WITH airdrop_addresses AS (
        SELECT DISTINCT to_address as address
        FROM airdrops
    )
    SELECT db.address, db.date, db.balance
    FROM adjusted_daily_balances db
    INNER JOIN airdrop_addresses aa ON db.address = aa.address
    """
    df = st.session_state.db_client.query_to_df_with_address_date_index(query)
   
    return df


def get_exchange_balances():
    """
    指定されたアドレスの全ての日付の残高を取得
    """
    addresses = [
        '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23',
        '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe'
    ]
    query = """
    SELECT address, date, balance
    FROM adjusted_daily_balances
    WHERE address IN ({})
    ORDER BY address, date
    """.format(','.join(['%s']*len(addresses)))

    df = st.session_state.db_client.query_to_df_with_address_date_index(query, params=tuple(addresses))

    return df

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
    df = st.session_state.db_client.query_to_df(query)
    return df


def get_daily_deposits():
    query = """
    SELECT 
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) as date,
        SUM(value / 1000000000000000000.0) as value,
        COUNT(DISTINCT from_address) as address_count,
        SUM(value / 1000000000000000000.0) / COUNT(DISTINCT from_address) as per_address
    FROM 
        deposits
    WHERE
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) >= '2024-09-26'
    GROUP BY 
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR))
    ORDER BY 
        date desc
    """
    df = st.session_state.db_client.query_to_df(query)
    
    return df



def get_daily_withdrawals():
    query = """
    SELECT 
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) as date,
        SUM(value / 1000000000000000000.0) as value,
        COUNT(DISTINCT to_address) as address_count,
        SUM(value / 1000000000000000000.0) / COUNT(DISTINCT to_address) as per_address
    FROM 
        withdrawals
    WHERE
        to_address != '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' and
        +DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) >= '2024-09-26'
    GROUP BY 
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR))
    ORDER BY 
        date desc
    """
    
    df = st.session_state.db_client.query_to_df(query)
    
    return df


def get_latest_timestamp() -> str:
    """
    geek_transactionsテーブルから最新のタイムスタンプを取得する
    
    :param db_file: データベースファイルのパス
    :return: 最新のタイムスタンプ（文字列形式）
    """

    
    query = """
    SELECT max(timestamp)
    FROM geek_transactions
    """
    
    result = st.session_state.db_client.fetch_one(query)
    
    return result[0]



def get_latest_balances_from_all_addresses():
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
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_latest_balances_from_airdrop_recipient():
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
    df = st.session_state.db_client.query_to_df(query)
    return df



def get_latest_balances_from_exchange():
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
    df = st.session_state.db_client.query_to_df(query, params=tuple(addresses))
    return df

def get_latest_balances_from_operator():
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
    df = st.session_state.db_client.query_to_df(query, params=tuple(addresses))
    return df

def get_latest_balances_from_game_ops_wallet():
    query = """
    SELECT balance
    FROM adjusted_daily_balances
    where address = '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62'
    ORDER BY date DESC
    LIMIT 1
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_latest_balances_from_withdrawal_wallet():
    query = """
    SELECT balance
    FROM adjusted_daily_balances
    where address = '0x687F3413C7f0e089786546BedF809b8F8885B051'
    ORDER BY date DESC
    LIMIT 1
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_latest_balances_from_airdrop_wallet():
    query = """
    SELECT balance
    FROM adjusted_daily_balances
    where address = '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7'
    ORDER BY date DESC
    LIMIT 1
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_latest_balances_from_others():
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
    
    df = st.session_state.db_client.query_to_df(query, params=tuple(operator_addresses + exchange_addresses))
    return df

def get_address_info(address: str):
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
            DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) as date,
            SUM(value / 1000000000000000000.0) as airdrop
        FROM airdrops
        WHERE 
            to_address = ? and 
            DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) >= '2024-09-26'
        GROUP BY DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR))
    ),
    withdraw as (   
        SELECT 
            DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) as date,
            SUM(value / 1000000000000000000.0) as withdraw
        FROM withdrawals
        WHERE 
            to_address = ? and
            DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) >= '2024-09-26'
        GROUP BY DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR))
    ),
    deposit as (
        SELECT 
            DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) as date,
            SUM(value / 1000000000000000000.0) as deposit
        FROM deposits
        WHERE 
            from_address = ? and 
            DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) >= '2024-09-26'
        GROUP BY DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR))
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
    df = st.session_state.db_client.query_to_df(query, params=(address, address, address, address))
    return df


def get_nft_sell_transactions(address:str):
    query = f"""
    SELECT from_address, value / 1000000000000000000.0 as value
    FROM geek_transactions
    WHERE to_address = '{address}' and
    timestamp between '2024-11-25T10:00:00.000000Z' and '2024-11-27T15:00:00.000000Z' and 
    method = 'transfer'
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_jst_4am_close_price():
    query = f"""
    SELECT timestamp, close
    FROM ohlcv_1h
    WHERE unix_timestamp(timestamp) % (24 * 60 * 60) = 18 * 60 * 60
    """
    df = st.session_state.db_client.query_to_df(query)
    return df


def get_nft_transactions():
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', None)
    # pd.set_option('display.max_colwidth', None)
    query = """
    with combined_results as (
        SELECT to_address, count(to_address) as count
        FROM nft_transactions
        where method = '0xe3456fbb'
        and timestamp between '2024-11-12 13:00:00' and '2024-11-12 15:59:59'
        or timestamp between '2024-11-19 13:00:00' and '2024-11-19 15:59:59'
        group by to_address

        union all

        SELECT to_address, count(to_address) as count
        FROM nft_transactions
        where method = 'safeTransferFrom'
        and timestamp < '2024-12-04 00:00:00'
        group by to_address
    )
    select to_address, sum(count) as count
    from combined_results
    group by to_address
    order by sum(count) desc
    """
    df = st.session_state.db_client.query_to_df(query)
    return df



#    count(date(datetime(timestamp))) date(datetime(timestamp))
# 0                                33                2024-11-08
# 1                               618                2024-11-12
# 2                                 1                2024-11-13
# 3                                22                2024-11-18
# 4                              1495                2024-11-19


# df = get_least_balances_from_all_addresses()
# print(df['balance'].sum())
# df = get_latest_balances_from_airdrop_recipient()
# print(df['balance'].sum())
# df = get_latest_balances_from_exchange()
# print(df['balance'].sum())
# df = get_latest_balances_from_others()
# print(df['balance'].sum())

