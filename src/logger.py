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
            f"{datetime.now().strftime('%Y%m%d')}_info.log"
        )
        
        # ファイルハンドラーの設定
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # フォーマッターの設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # ハンドラーの追加
        logger.addHandler(file_handler)

         # ---------- エラーログ (ERROR以上) 用のファイルハンドラー ----------
        error_log_file = os.path.join(
            log_dir, 
            f"{datetime.now().strftime('%Y%m%d')}_error.log"
        )
        error_file_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        logger.addHandler(error_file_handler)

        # ---------- デバッグログ (DEBUG以上) 用のファイルハンドラー ----------
        debug_log_file = os.path.join(
            log_dir, 
            f"{datetime.now().strftime('%Y%m%d')}_debug.log"
        )
        debug_file_handler = RotatingFileHandler(
            debug_log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(formatter)
        logger.addHandler(debug_file_handler)

        # ---------- コンソールハンドラー ----------

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    
    return logger