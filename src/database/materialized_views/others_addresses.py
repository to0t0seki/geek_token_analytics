from src.database.data_access.database_client import DatabaseClient


def create_others_addresses(db_client: DatabaseClient) -> None:
    params = {
        'address1': '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7',  # Airdrop_Wallet
        'address2': '0x687F3413C7f0e089786546BedF809b8F8885B051',  # Withdrawal_Wallet
        'address3': '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62',   # Game_Ops_Wallet
        'address4': '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23',   #bitget
        'address5': '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe',   #gate
        'address6': '0x188b3678a4E706D17D060E6FCFbfec359e4bb69a'   #geek_shop
    }

    create_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS others_addresses AS
    WITH excluded_addresses AS (
        SELECT %(address1)s as address
        UNION ALL SELECT %(address2)s as address
        UNION ALL SELECT %(address3)s as address
        UNION ALL SELECT %(address4)s as address
        UNION ALL SELECT %(address5)s as address
        UNION ALL SELECT %(address6)s as address
        UNION ALL SELECT '0x0000000000000000000000000000000000000000' as address
        UNION ALL
        SELECT address
        FROM users_addresses
    )
    SELECT lb.address
    FROM latest_balances as lb
    LEFT JOIN excluded_addresses ea ON lb.address = ea.address
    WHERE ea.address IS NULL
    """
    db_client.execute(create_query, params)


    create_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_others_addresses_address 
    ON others_addresses(address);
    """
    db_client.execute(create_index_query)
    print("others_addressesを作成しました。")


def refresh_others_addresses(db_client: DatabaseClient) -> None:
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY others_addresses;
    """
    db_client.execute(refresh_query)

if __name__ == "__main__":
    client = DatabaseClient()
    create_others_addresses(client)



