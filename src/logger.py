import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """アプリケーション用のロガーをセットアップする"""
    
    # ログディレクトリが存在しない場合は作成
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # ロガーの作成
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 既存のハンドラーがある場合は追加しない
    if not logger.handlers:
        # 日付ベースのログファイル名
        log_file = os.path.join(
            log_dir, 
            f"{datetime.now().strftime('%Y%m%d')}_{name}.log"
        )
        
        # ファイルハンドラーの設定
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # フォーマッターの設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # ハンドラーの追加
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    
    return logger