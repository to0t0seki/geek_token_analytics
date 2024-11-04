import unittest
import json
import os
from unittest.mock import patch, MagicMock
from src.data_collection.geek_transfers import update_geek_transfers, load_existing_transfers

class TestGeekTransfers(unittest.TestCase):

    def setUp(self):
        # テスト用のデータディレクトリを作成
        os.makedirs('data/raw', exist_ok=True)

    def tearDown(self):
        # テスト用のファイルを削除
        if os.path.exists('data/raw/test_transfers.json'):
            os.remove('data/raw/test_transfers.json')

    def test_load_existing_transfers_empty(self):
        # 既存のファイルがない場合、空のリストが返されることをテスト
        transfers = load_existing_transfers('non_existent_file.json')
        self.assertEqual(transfers, [])

    def test_load_existing_transfers(self):
        # 既存のファイルがある場合、正しくロードされることをテスト
        test_data = [{"tx_hash": "0x123", "timestamp": "2023-01-01T00:00:00Z"}]
        with open('data/raw/test_transfers.json', 'w') as f:
            json.dump(test_data, f)
        
        transfers = load_existing_transfers('test_transfers.json')
        self.assertEqual(transfers, test_data)

    @patch('src.data_collection.geek_transfers.requests.get')
    def test_update_geek_transfers_new_data(self, mock_get):
        # 新しいデータがある場合のテスト
        existing_data = [{"tx_hash": "0x123", "timestamp": "2023-01-01T00:00:00Z"}]
        with open('data/raw/test_transfers.json', 'w') as f:
            json.dump(existing_data, f)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"tx_hash": "0x456", "timestamp": "2023-01-02T00:00:00Z"},
                {"tx_hash": "0x123", "timestamp": "2023-01-01T00:00:00Z"}
            ],
            "next_page_params": None
        }
        mock_get.return_value = mock_response

        new_items = update_geek_transfers('test_transfers.json')
        self.assertEqual(len(new_items), 1)
        self.assertEqual(new_items[0]['tx_hash'], "0x456")

        # ファイルが正しく更新されたことを確認
        with open('data/raw/test_transfers.json', 'r') as f:
            updated_data = json.load(f)
        self.assertEqual(len(updated_data), 2)
        self.assertEqual(updated_data[0]['tx_hash'], "0x456")

    @patch('src.data_collection.geek_transfers.requests.get')
    def test_update_geek_transfers_no_new_data(self, mock_get):
        # 新しいデータがない場合のテスト
        existing_data = [{"tx_hash": "0x123", "timestamp": "2023-01-01T00:00:00Z"}]
        with open('data/raw/test_transfers.json', 'w') as f:
            json.dump(existing_data, f)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"tx_hash": "0x123", "timestamp": "2023-01-01T00:00:00Z"}
            ],
            "next_page_params": None
        }
        mock_get.return_value = mock_response

        new_items = update_geek_transfers('test_transfers.json')
        self.assertEqual(len(new_items), 0)

        # ファイルが変更されていないことを確認
        with open('data/raw/test_transfers.json', 'r') as f:
            updated_data = json.load(f)
        self.assertEqual(updated_data, existing_data)

if __name__ == '__main__':
    unittest.main()