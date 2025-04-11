from src.database.data_access.database_client import DatabaseClient

def create_vw_others_transactions(client: DatabaseClient) -> None:
    
    params = {
        'address1': '0xdA364EE05bC0E37b838ebf1ba8AB2051dc187Dd7',   # Airdrop_Wallet
        'address2': '0x687F3413C7f0e089786546BedF809b8F8885B051',   #Withdrawal_Wallet
        'address3': '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62',   #Game_Ops_Wallet
        'address4': '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23',   #bitget
        'address5': '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe',   #gate
        'address6': '0x188b3678a4E706D17D060E6FCFbfec359e4bb69a'   #geek_shop
    }

          
    create_view = """
    CREATE OR REPLACE VIEW vw_others_transactions AS
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
    select gt.* from geek_transactions gt
    left join excluded_addresses ea on gt.from_address = ea.address
    left join excluded_addresses eb on gt.to_address = eb.address
    where ea.address is null or eb.address is null
    """
    client.execute(create_view, params)
    print("vw_others_transactionsを作成しました。")
        


if __name__ == "__main__":
    create_vw_others_transactions(DatabaseClient())