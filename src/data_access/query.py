import streamlit as st


def get_airdrop_recipient_balances():
    """
    airdropsテーブルにあるアドレスの全ての日付の残高を取得
    """
    query = """
    SELECT db.date, sum(db.balance / 1e18) as balance
    FROM daily_balances db
    INNER JOIN airdrop_recipients ar ON db.address = ar.address
    where db.date > '2024-09-26'
    group by db.date
    order by db.date desc
    """
    df = st.session_state.db_client.query_to_df(query)
 
    return df


def get_daily_airdrops():   
    query = """
    SELECT 
        DATE(timestamp + INTERVAL '5 hours') as date,
        SUM(value / 1e18) as value,
        COUNT(DISTINCT to_address) as address_count
    FROM 
        airdrops
    WHERE
        DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
    GROUP BY 
        DATE(timestamp + INTERVAL '5 hours')
    ORDER BY 
        date desc
    """
    df = st.session_state.db_client.query_to_df(query)
    return df


def get_daily_deposits():
    query = """
    SELECT 
        DATE(timestamp + INTERVAL '5 hours') as date,
        SUM(value / 1e18) as value,
        COUNT(DISTINCT from_address) as address_count
    FROM 
        deposits
    WHERE
        DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
    GROUP BY 
        DATE(timestamp + INTERVAL '5 hours')
    ORDER BY 
        date desc
    """
    df = st.session_state.db_client.query_to_df(query)

    return df



def get_daily_withdrawals():
    query = """
    SELECT 
        DATE(timestamp + INTERVAL '5 hours') as date,
        SUM(value / 1e18) as value,
        COUNT(DISTINCT to_address) as address_count
    FROM 
        withdrawals
    WHERE
        to_address != '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' and
        DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
    GROUP BY 
        DATE(timestamp + INTERVAL '5 hours')
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
        date,
        address,
        balance / 1e18 as balance
    FROM latest_balances
    WHERE address != '0x0000000000000000000000000000000000000000'
    ORDER BY balance DESC
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_latest_balances_from_airdrop_recipient():
    """
    エアドロップを一度でも受け取ったことがあるアドレスの最新の残高を取得
    """
    query = """
    SELECT lb.address, lb.date, lb.balance / 1e18 as balance
    FROM latest_balances as lb
    INNER JOIN airdrop_recipients as apd ON lb.address = apd.address
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
    SELECT lb.address, lb.date, lb.balance / 1e18 as balance
    FROM latest_balances as lb
    INNER JOIN (
        SELECT %(address1)s as address
        UNION ALL
        SELECT %(address2)s
    ) as exd ON lb.address = exd.address
    """
    params = {'address1':addresses[0], 'address2':addresses[1]}
    df = st.session_state.db_client.query_to_df(query, params=params)
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
    SELECT lb.address, lb.date, lb.balance / 1e18 as balance
    FROM latest_balances as lb
    INNER JOIN (
        SELECT %(address1)s as address
        UNION ALL
        SELECT %(address2)s
        UNION ALL
        SELECT %(address3)s
    ) as op ON lb.address = op.address
    """
    params = {'address1':addresses[0], 'address2':addresses[1], 'address3':addresses[2]}
    df = st.session_state.db_client.query_to_df(query, params=params)
    return df

def get_latest_balances_from_game_ops_wallet():
    query = """
    SELECT lb.balance / 1e18 as balance
    FROM latest_balances as lb
    where lb.address = '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62'
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_latest_balances_from_withdrawal_wallet():
    query = """
    SELECT lb.balance / 1e18 as balance
    FROM latest_balances as lb
    where lb.address = '0x687F3413C7f0e089786546BedF809b8F8885B051'
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_latest_balances_from_airdrop_wallet():
    query = """
    SELECT lb.balance / 1e18 as balance
    FROM latest_balances as lb
    where lb.address = '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7'
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
    WITH excluded_addresses AS (
        SELECT %(address1)s as address
        UNION ALL SELECT %(address2)s as address
        UNION ALL SELECT %(address3)s as address
        UNION ALL SELECT %(address4)s as address
        UNION ALL SELECT %(address5)s as address
        UNION ALL SELECT '0x0000000000000000000000000000000000000000' as address
        UNION ALL
        SELECT address
        FROM airdrop_recipients
    )
    SELECT lb.address, lb.date, lb.balance / 1e18 as balance
    FROM latest_balances as lb
    LEFT JOIN excluded_addresses ea ON lb.address = ea.address
    WHERE ea.address IS NULL
    """
    params = {'address1':operator_addresses[0], 'address2':operator_addresses[1], 'address3':operator_addresses[2], 'address4':exchange_addresses[0], 'address5':exchange_addresses[1]}
    df = st.session_state.db_client.query_to_df(query, params=params)
    return df

def get_address_info(address: str):
    """
    指定されたアドレスの情報を取得
    """
    query = """
    WITH balances AS (
        SELECT date, balance as balance
        FROM daily_balances
        WHERE address = %(address)s and date >= '2024-09-26'
    ),
    airdrop as (
        SELECT 
            DATE(timestamp + INTERVAL '5 hours') as date,
            SUM(value / 1e18) as airdrop
        FROM airdrops
        WHERE 
            to_address = %(address)s and 
            DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
        GROUP BY DATE(timestamp + INTERVAL '5 hours')
    ),
    withdraw as (   
        SELECT 
            DATE(timestamp + INTERVAL '5 hours') as date,
            SUM(value / 1e18) as withdraw
        FROM withdrawals
        WHERE 
            to_address = %(address)s and
            DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
        GROUP BY DATE(timestamp + INTERVAL '5 hours')
    ),
    deposit as (
        SELECT 
            DATE(timestamp + INTERVAL '5 hours') as date,
            SUM(value / 1e18) as deposit
        FROM deposits
        WHERE 
            from_address = %(address)s and 
            DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
        GROUP BY DATE(timestamp + INTERVAL '5 hours')
    )
    SELECT 
        b.date,
        b.balance / 1e18 as balance,
        COALESCE(a.airdrop, 0) as airdrop,
        COALESCE(w.withdraw, 0) as withdraw,
        COALESCE(d.deposit, 0) as deposit
    FROM balances b
    LEFT JOIN airdrop a ON b.date = a.date
    LEFT JOIN withdraw w ON b.date = w.date
    LEFT JOIN deposit d ON b.date = d.date
    ORDER BY b.date DESC    
    """
    params = {'address':address}
    df = st.session_state.db_client.query_to_df(query, params=params)
    return df



def get_nft_sell_transactions(address:str):
    query = f"""
    SELECT from_address, value / 1e18 as value
    FROM geek_transactions
    WHERE to_address = '{address}' and
    timestamp between '2024-11-25T10:00:00.000000Z' and '2024-11-27T15:00:00.000000Z' and 
    method = 'transfer'
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_jst_4am_close_price():
    query = """
    (SELECT date(timestamp + INTERVAL '5 hours') as date, close
    FROM ohlcv_1h
    WHERE EXTRACT(HOUR FROM timestamp) = 18
    union
    (SELECT date(timestamp + INTERVAL '5 hours') as date, close
    FROM ohlcv_1h
    order by timestamp desc
    limit 1))
    order by date desc
    """
    df = st.session_state.db_client.query_to_df(query)
    return df

def get_latest_geek_price():
    query = """
    SELECT close
    FROM ohlcv_1h
    ORDER BY timestamp DESC
    LIMIT 1
    """
    result = st.session_state.db_client.fetch_one(query)
    return result[0]

def get_nft_transactions():
    query = """
    with combined_results as (
        SELECT to_address, count(to_address) as count
        FROM nft_transactions
        where method = '0xe3456fbb'
        and (timestamp between '2024-11-12 13:00:00' and '2024-11-12 15:59:59'
        or timestamp between '2024-11-19 13:00:00' and '2024-11-19 15:59:59')
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

