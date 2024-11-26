# Geek_Analytics
## 環境設定
### 開発環境のセットアップ
1. 開発環境用の依存パッケージをインストール

bash
pip install -r requirements.txt

2. 開発環境の設定を適用

bash
python scripts/setup_config.py


### 本番環境のセットアップ

1. 本番環境用の依存パッケージをインストール

bash
pip install -r requirements.txt

2. 本番環境の設定を適用

bash
Linux/Mac
ENV=production python scripts/setup_config.py
Windows (Command Prompt)
set ENV=production && python scripts/setup_config.py
Windows (PowerShell)
$env:ENV = "production"; python scripts/setup_config.py

## プロジェクト構成

plaintext
your_project/
├── .streamlit/
│ ├── config.production.toml # 本番環境用の設定
│ └── config.development.toml # 開発環境用の設定
├── scripts/
│ └── setup_config.py # 設定切り替えスクリプト
├── src/
│ └── app.py # アプリケーションのメインファイル
├── requirements.txt # 本番環境用の依存パッケージ
├── requirements-dev.txt # 開発環境用の依存パッケージ
└── README.md


## 設定ファイルについて

### Streamlit設定

- `.streamlit/config.development.toml`: 開発環境用の設定
  ```toml
  [server]
  address = "localhost"
  port = 8501
  headless = false
  ```

- `.streamlit/config.production.toml`: 本番環境用の設定
  ```toml
  [server]
  address = "0.0.0.0"
  port = 8501
  headless = true
  ```

### 依存パッケージ

- `requirements.txt`: 本番環境で必要な依存パッケージ
- `requirements-dev.txt`: 開発環境で追加で必要な依存パッケージ（テストツール、開発ツールなど）

## 環境変数

- `ENV`: 実行環境を指定する環境変数
  - `development`: 開発環境（デフォルト）
  - `production`: 本番環境

## 注意事項

- `.streamlit/config.toml`は自動生成されるファイルのため、バージョン管理には含めません。
- 開発環境では`requirements-dev.txt`をインストールすることで、`requirements.txt`の依存パッケージも自動的にインストールされます。