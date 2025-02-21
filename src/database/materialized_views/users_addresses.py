from src.database.data_access.database_client import DatabaseClient


def create_users_addresses(db_client: DatabaseClient) -> None:
    create_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS users_addresses AS
    SELECT DISTINCT to_address as address
    FROM vw_airdrops
    """
    db_client.execute(create_query)

    create_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_addresses_address 
    ON users_addresses(address);
    """
    db_client.execute(create_index_query)
    print("users_addressesを作成しました。")

def refresh_users_addresses(db_client: DatabaseClient) -> None:
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY users_addresses;
    """
    db_client.execute(refresh_query)

if __name__ == "__main__":
    client = DatabaseClient()
    create_users_addresses(client)


