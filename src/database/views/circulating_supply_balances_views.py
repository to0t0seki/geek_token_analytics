from src.database.data_access.database_client import DatabaseClient

def create_vw_circulating_supply_balances(client: DatabaseClient) -> None:

    params = {
        'address1': '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7', # Airdrop_Wallet
        'address2': '0x687F3413C7f0e089786546BedF809b8F8885B051', # Withdrawal_Wallet
        'address3': '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62', # Game_Ops_Wallet
        'address4': '0x188b3678a4E706D17D060E6FCFbfec359e4bb69a', #game_item_wallet
    }

          

    create_view = """
    CREATE OR REPLACE VIEW vw_circulating_supply_balances AS
    WITH excluded_addresses AS (
        SELECT %(address1)s as address
        UNION ALL SELECT %(address2)s as address
        UNION ALL SELECT %(address3)s as address
        UNION ALL SELECT %(address4)s as address
        UNION ALL SELECT '0x0000000000000000000000000000000000000000' as address
    )
    SELECT db.*
    FROM daily_balances as db
    LEFT JOIN excluded_addresses ea ON db.address = ea.address
    WHERE ea.address IS NULL
    """
    client.execute(create_view, params)

    print("vw_circulating_supply_balancesを作成しました。")
        


if __name__ == "__main__":
    create_vw_circulating_supply_balances(DatabaseClient())