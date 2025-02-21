from src.database.data_access.database_client import DatabaseClient

def get_users_addresses_balances(db_client: DatabaseClient):
    """
    ユーザーゲームウォレットの全ての日付の残高を取得
    """
    query = """
    SELECT date, sum(balance / 1e18) as balance
    FROM vw_users_balances
    where date > '2024-09-26'
    group by date
    order by date desc
    """
    df = db_client.query_to_df(query)
 
    return df

def get_others_addresses_balances(db_client: DatabaseClient):
    """
    運営、取引所、ユーザー以外のアドレスの全ての日付の残高を取得
    """
    query = """
    SELECT date, sum(balance / 1e18) as balance
    FROM vw_others_balances
    where date > '2024-09-26'
    group by date
    order by date desc
    """
    df = db_client.query_to_df(query)
 
    return df

def get_daily_airdrops(db_client: DatabaseClient):   
    query = """
    SELECT 
        DATE(timestamp + INTERVAL '5 hours') as date,
        SUM(value / 1e18) as value,
        COUNT(DISTINCT to_address) as address_count
    FROM 
        vw_airdrops
    WHERE
        DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
    GROUP BY 
        DATE(timestamp + INTERVAL '5 hours')
    ORDER BY 
        date desc
    """
    df = db_client.query_to_df(query)
    return df


def get_daily_deposits(db_client: DatabaseClient):
    query = """
    SELECT 
        DATE(timestamp + INTERVAL '5 hours') as date,
        SUM(value / 1e18) as value,
        COUNT(DISTINCT from_address) as address_count
    FROM 
        vw_deposits
    WHERE
        DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
    GROUP BY 
        DATE(timestamp + INTERVAL '5 hours')
    ORDER BY 
        date desc
    """
    df = db_client.query_to_df(query)

    return df



def get_daily_withdrawals(db_client: DatabaseClient):
    query = """
    SELECT 
        DATE(timestamp + INTERVAL '5 hours') as date,
        SUM(value / 1e18) as value,
        COUNT(DISTINCT to_address) as address_count
    FROM 
        vw_withdrawals
    WHERE
        to_address != '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' and
        DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
    GROUP BY 
        DATE(timestamp + INTERVAL '5 hours')
    ORDER BY 
        date desc
    """
    
    df = db_client.query_to_df(query)
    
    return df


def get_latest_timestamp(db_client: DatabaseClient) -> str:
    """
    geek_transactionsテーブルから最新のタイムスタンプを取得する
    
    :param db_file: データベースファイルのパス
    :return: 最新のタイムスタンプ（文字列形式）
    """

    
    query = """
    SELECT max(timestamp)
    FROM geek_transactions
    """
    
    result = db_client.fetch_one(query)
    
    return result[0]



def get_latest_balances_from_all_addresses(db_client: DatabaseClient):
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
    df = db_client.query_to_df(query)
    return df

def get_latest_balances_from_users(db_client: DatabaseClient):
    """
    エアドロップを一度でも受け取ったことがあるアドレスの最新の残高を取得
    """
    query = """
    SELECT lb.address, lb.date, lb.balance / 1e18 as balance
    FROM latest_balances as lb
    INNER JOIN users_addresses as ua ON lb.address = ua.address
    """
    df = db_client.query_to_df(query)
    return df



def get_latest_balances_from_exchange(db_client: DatabaseClient):
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
    df = db_client.query_to_df(query, params=params)
    return df

def get_latest_balances_from_operator(db_client: DatabaseClient):
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
    df = db_client.query_to_df(query, params=params)
    return df

def get_latest_balances_from_game_ops_wallet(db_client: DatabaseClient):
    query = """
    SELECT lb.balance / 1e18 as balance
    FROM latest_balances as lb
    where lb.address = '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62'
    """
    df = db_client.query_to_df(query)
    return df

def get_latest_balances_from_withdrawal_wallet(db_client: DatabaseClient):
    query = """
    SELECT lb.balance / 1e18 as balance
    FROM latest_balances as lb
    where lb.address = '0x687F3413C7f0e089786546BedF809b8F8885B051'
    """
    df = db_client.query_to_df(query)
    return df

def get_latest_balances_from_airdrop_wallet(db_client: DatabaseClient):
    query = """
    SELECT lb.balance / 1e18 as balance
    FROM latest_balances as lb
    where lb.address = '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7'
    """
    df = db_client.query_to_df(query)
    return df

def get_latest_balances_from_others(db_client: DatabaseClient):
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
        FROM users_addresses
    )
    SELECT lb.address, lb.date, lb.balance / 1e18 as balance
    FROM latest_balances as lb
    LEFT JOIN excluded_addresses ea ON lb.address = ea.address
    WHERE ea.address IS NULL
    """
    params = {'address1':operator_addresses[0], 'address2':operator_addresses[1], 'address3':operator_addresses[2], 'address4':exchange_addresses[0], 'address5':exchange_addresses[1]}
    df = db_client.query_to_df(query, params=params)
    return df

def get_address_info(db_client: DatabaseClient, address: str):
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
        FROM vw_airdrops
        WHERE 
            to_address = %(address)s and 
            DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
        GROUP BY DATE(timestamp + INTERVAL '5 hours')
    ),
    withdraw as (   
        SELECT 
            DATE(timestamp + INTERVAL '5 hours') as date,
            SUM(value / 1e18) as withdraw
        FROM vw_withdrawals
        WHERE 
            to_address = %(address)s and
            DATE(timestamp + INTERVAL '5 hours') >= '2024-09-26'
        GROUP BY DATE(timestamp + INTERVAL '5 hours')
    ),
    deposit as (
        SELECT 
            DATE(timestamp + INTERVAL '5 hours') as date,
            SUM(value / 1e18) as deposit
        FROM vw_deposits
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
    df = db_client.query_to_df(query, params=params)
    return df



def get_nft_sell_transactions(db_client: DatabaseClient, address:str):
    query = f"""
    SELECT from_address, value / 1e18 as value
    FROM geek_transactions
    WHERE to_address = '{address}' and
    timestamp between '2024-11-25T10:00:00.000000Z' and '2024-11-27T15:00:00.000000Z' and 
    method = 'transfer'
    """
    df = db_client.query_to_df(query)
    return df

def get_jst_4am_close_price(db_client: DatabaseClient):
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
    df = db_client.query_to_df(query)
    return df


def get_nft_transactions(db_client: DatabaseClient):
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
    df = db_client.query_to_df(query)
    return df


def get_withdrawal_ranking_1(db_client: DatabaseClient):
    query = """
        select to_address, 
        count(distinct tx_hash),
        round(sum(value/1e18)) as value 
        from geek_transactions 
        where method='exportToken' 
        and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
        and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
        or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
        or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
        and timestamp + interval'9hour' between '2025-01-11 04:00:00' and '2025-02-15 04:00:00'
        group by to_address
    """
    df = db_client.query_to_df(query)
    return df

def get_withdrawal_transactions_1(db_client: DatabaseClient):
    query = """
        select 
        tx_hash,
        to_address as address,
        timestamp + interval'9hour' as timestamp,
        count(tx_hash),
        round(sum(value/1e18)) as value 
        from geek_transactions 
        where method='exportToken' 
        and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
        and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
        or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
        or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
        and timestamp + interval'9hour' between '2025-01-11 04:00:00' and '2025-02-15 04:00:00'
        group by tx_hash,to_address,timestamp
    """
    df = db_client.query_to_df(query)
    return df

def get_withdrawal_ranking_in_usdt_1(db_client: DatabaseClient):
    query = """
        with withdrawal_transactions as (
        select to_address, 
        tx_hash,
        timestamp,
        round(value/1e18) as value 
        from geek_transactions 
        where method='exportToken' 
        and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
        and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
        or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
        or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
        and timestamp + interval'9hour' between '2025-01-11 04:00:00' and '2025-02-15 04:00:00'
        ),
        withdrawal_transactions_with_close as (
        select withdrawal_transactions.*, ohlcv_1h.close, round(withdrawal_transactions.value * ohlcv_1h.close,2) as value_usd
        from withdrawal_transactions
        left join ohlcv_1h on date_trunc('hour', withdrawal_transactions.timestamp) = date_trunc('hour', ohlcv_1h.timestamp + interval'1hour')
        )
        select to_address, count(distinct tx_hash), round(sum(value_usd),1) as value_usd
        from withdrawal_transactions_with_close
        group by to_address
    """
    df = db_client.query_to_df(query)
    return df

def get_withdrawal_transactions_in_usdt_1(db_client: DatabaseClient):
    query = """
        with withdrawal_transactions as (
        select 
        tx_hash,
        to_address as address,
        timestamp + interval'9hour' as timestamp,
        count(tx_hash),
        round(sum(value/1e18)) as value 
        from geek_transactions 
        where method='exportToken' 
        and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
        and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
        or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
        or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
        and timestamp + interval'9hour' between '2025-01-11 04:00:00' and '2025-02-15 04:00:00'
        group by tx_hash,to_address,timestamp
    )
    select withdrawal_transactions.*, ohlcv_1h.close, round(withdrawal_transactions.value * ohlcv_1h.close,1) as value_usd
    from withdrawal_transactions
    left join ohlcv_1h on date_trunc('hour', withdrawal_transactions.timestamp) = date_trunc('hour', ohlcv_1h.timestamp + interval'10hour')
    """
    df = db_client.query_to_df(query)
    return df


def get_withdrawal_ranking_2(db_client: DatabaseClient):
    query = """
        select to_address, 
        count(distinct tx_hash),
        round(sum(value/1e18)) as value 
        from geek_transactions 
        where method='exportToken' 
        and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
        and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
        or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
        or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
        and timestamp + interval'9hour' > '2025-02-15 04:00:00'
        group by to_address
    """
    df = db_client.query_to_df(query)
    return df

def get_withdrawal_transactions_2(db_client: DatabaseClient):
    query = """
        select 
        tx_hash,
        to_address as address,
        timestamp + interval'9hour' as timestamp,
        count(tx_hash),
        round(sum(value/1e18)) as value 
        from geek_transactions 
        where method='exportToken' 
        and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
        and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
        or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
        or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
        and timestamp + interval'9hour' > '2025-02-15 04:00:00'
        group by tx_hash,to_address,timestamp
    """
    df = db_client.query_to_df(query)
    return df

def get_withdrawal_ranking_in_usdt_2(db_client: DatabaseClient):
    query = """
        with withdrawal_transactions as (
        select to_address, 
        tx_hash,
        timestamp,
        round(value/1e18) as value 
        from geek_transactions 
        where method='exportToken' 
        and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
        and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
        or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
        or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
        and timestamp + interval'9hour' > '2025-02-15 04:00:00'
        ),
        withdrawal_transactions_with_close as (
        select withdrawal_transactions.*, ohlcv_1h.close, round(withdrawal_transactions.value * ohlcv_1h.close,1) as value_usd
        from withdrawal_transactions
        left join ohlcv_1h on date_trunc('hour', withdrawal_transactions.timestamp) = date_trunc('hour', ohlcv_1h.timestamp + interval'1hour')
        )
        select to_address, count(distinct tx_hash), round(sum(value_usd),2) as value_usd
        from withdrawal_transactions_with_close
        group by to_address
    """
    df = db_client.query_to_df(query)
    return df

def get_withdrawal_transactions_in_usdt_2(db_client: DatabaseClient):
    query = """
        with withdrawal_transactions as (
        select 
        tx_hash,
        to_address as address,
        timestamp + interval'9hour' as timestamp,
        count(tx_hash),
        round(sum(value/1e18)) as value 
        from geek_transactions 
        where method='exportToken' 
        and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
        and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
        or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
        or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
        and timestamp + interval'9hour' > '2025-02-15 04:00:00'
        group by tx_hash,to_address,timestamp
    )
    select withdrawal_transactions.*, ohlcv_1h.close, round(withdrawal_transactions.value * ohlcv_1h.close,1) as value_usd
    from withdrawal_transactions
    left join ohlcv_1h on date_trunc('hour', withdrawal_transactions.timestamp) = date_trunc('hour', ohlcv_1h.timestamp + interval'10hour')
    """
    df = db_client.query_to_df(query)
    return df

#    count(date(datetime(timestamp))) date(datetime(timestamp))
# 0                                33                2024-11-08
# 1                               618                2024-11-12
# 2                                 1                2024-11-13
# 3                                22                2024-11-18
# 4                              1495                2024-11-19


# df = get_least_balances_from_all_addresses()
# print(df['balance'].sum())
# df = get_latest_balances_from_users()
# print(df['balance'].sum())
# df = get_latest_balances_from_exchange()
# print(df['balance'].sum())
# df = get_latest_balances_from_others()
# print(df['balance'].sum())


#出金アリーナ全ての時間のランキング
# query = """
#  select to_address, 
#  count(to_address),
#  round(sum(value/1e18)) as value 
#  from geek_transactions 
#  where method='exportToken' 
#  and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
#  and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
#  or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
#  or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
#  and timestamp + interval'9hour' > '2025-01-11 04:00:00' 
#  group by to_address 
#  order by round(sum(value/1e18)) desc;
# """





#出金アリーナ全ての時間の履歴
# query = """
# select timestamp + interval '9hour' as timestamp,
# from_address,
# to_address ,
# round(value/1e18) as value
# from geek_transactions 
# where method='exportToken' 
# and to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62'
# and ((timestamp + interval'9hour')::time between '04:04:00' and '04:04:20' 
# or (timestamp + interval'9hour')::time between '12:00:00' and '12:00:20' 
# or (timestamp + interval'9hour')::time between '20:00:00' and '20:00:20') 
# and timestamp + interval'9hour' > '2025-01-11 04:00:00' 
# order by timestamp desc;
# """

#出金アリーナ4時の時間帯のトータル出金額
# query = """
# select (timestamp + interval '9hour')::date as timestamp, 
# round(sum(value/1e18)) as value 
# from geek_transactions 
# where method='exportToken' and 
# to_address!='0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62' 
# and (timestamp + interval'9hour')::time between '04:04:00' and '04:04:19' 
# and timestamp + interval'9hour' > '2025-01-11 04:00:00' 
# group by (timestamp + interval'9hour')::date 
# order by timestamp desc;
# """
