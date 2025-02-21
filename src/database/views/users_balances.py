from src.database.data_access.database_client import DatabaseClient

def create_vw_users_balances(client: DatabaseClient) -> None:

    create_view = """
    CREATE OR REPLACE VIEW vw_users_balances AS
    SELECT db.*
    FROM daily_balances db
    INNER JOIN users_addresses ua ON db.address = ua.address
    """
    client.execute(create_view)

    print("vw_users_balancesを作成しました。")
        


if __name__ == "__main__":
    create_vw_users_balances(DatabaseClient())