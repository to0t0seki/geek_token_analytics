from src.database.data_access.database_client import DatabaseClient

# データベースクライアントを作成
db_client = DatabaseClient()

# SQLコマンドを実行
db_client.execute("ALTER TABLE geek_transactions ALTER COLUMN method TYPE VARCHAR(30);")
db_client.execute("ALTER TABLE geek_transactions_oas ALTER COLUMN method TYPE VARCHAR(30);")
db_client.execute("ALTER TABLE equipment_transactions ALTER COLUMN method TYPE VARCHAR(30);")
db_client.execute("ALTER TABLE doll_transactions ALTER COLUMN method TYPE VARCHAR(30);")
# 接続を閉じる
# db_client.close()