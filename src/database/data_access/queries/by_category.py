from src.database.data_access.database_client import DatabaseClient

def get_all(db_client: DatabaseClient):
    """
    全てのアドレスの日時残高推移
    """
    query = """
    SELECT 
      date as date,
      sum(balance / 1e18) as balance
    FROM daily_balances
    where date > '2024-09-26'
    and address != '0x0000000000000000000000000000000000000000'
    group by date
    order by date desc
    """
    df = db_client.query_to_df(query)
    return df



def get_game_wallet(db_client: DatabaseClient):
    """
    ゲームウォレットの日時残高推移
    """
    query = """
    SELECT 
      db.date,
      sum(db.balance / 1e18) as balance
    FROM daily_balances db
    JOIN addresses a ON db.address = a.address
    WHERE db.date > '2024-09-26'
    and a.main_type = 'game_wallet'
    group by db.date
    order by db.date desc
    """
    df = db_client.query_to_df(query)
    return df

def get_admin(db_client: DatabaseClient):
    """
    運営、取引所、ユーザー以外のアドレスの全ての日付の残高を取得
    """
    query = """
    SELECT date, sum(balance / 1e18) as balance
    FROM daily_balances as db
    JOIN addresses a ON db.address = a.address
    where db.date > '2024-09-26'
    and a.main_type = 'admin'
    group by db.date
    order by db.date desc
    """
    df = db_client.query_to_df(query)
    return df

def get_exchange(db_client: DatabaseClient):
    """
    取引所の日時残高推移
    """
    query = """
    SELECT date, sum(balance / 1e18) as balance
    FROM daily_balances as db
    JOIN addresses a ON db.address = a.address
    where db.date > '2024-09-26'
    and a.main_type = 'exchange'
    group by db.date
    order by db.date desc
    """
    df = db_client.query_to_df(query)
    return df


def get_others(db_client: DatabaseClient):
    """
    運営、取引所、ユーザー以外のアドレスの全ての日付の残高を取得
    """
    query = """
    SELECT date, sum(balance / 1e18) as balance
    FROM daily_balances as db
    LEFT JOIN addresses a ON db.address = a.address
    where db.date > '2024-09-26'
    and a.main_type is null
    group by db.date
    order by db.date desc
    """
    df = db_client.query_to_df(query)
 
    return df

def get_circulating_supply(db_client: DatabaseClient):
    """
    循環供給を取得
    """
    query = """
    SELECT date, sum(balance / 1e18) as balance
    FROM daily_balances db
    LEFT JOIN addresses a ON db.address = a.address
    where date > '2024-09-26'
    and a.main_type not in ('admin', 'burn')
    group by date
    order by date desc
    """
    df = db_client.query_to_df(query)

    return df

