#!/usr/bin/env python3
"""
このスクリプトは、logsディレクトリ内にある全ての
YYYYMMDD_main_error.log 形式のエラーログファイルをチェックし、
ファイル内にエラー出力が存在する場合に標準出力へ出力します。
"""

import glob
import os

def check_all_error_logs(log_dir: str = "logs", logger_name: str = "__main__") -> None:
    """
    logsディレクトリ内の全てのYYYYMMDD_main_error.log形式のログファイルをチェックし、
    エラー出力がある場合、その内容を標準出力に出力する関数。

    Parameters:
        log_dir (str): ログディレクトリへのパス。
        logger_name (str): ロガーの名前（ログファイル名に使用）。
    """
    # ファイルパターン作成：ファイル名は8桁の日付 + "_" + logger_name + "_error.log"
    # 例: 20231012_main_error.log
    pattern = os.path.join(log_dir, "????????_" + logger_name + "_error.log")
    
    # パターンに一致するファイル一覧を取得
    log_files = glob.glob(pattern)
    
    if not log_files:
        print("指定されたパターンに一致するエラーログファイルは存在しません。")
        return

    # ファイル名を昇順（古い順）にソート
    for log_file in sorted(log_files):
        print(f"\n---- ログファイル: {log_file} ----")
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"ファイルの読み込み中にエラーが発生しました: {e}")
            continue

        # 空白や改行のみの場合はエラー出力なしと見なす
        if content.strip():
            print(content)
        else:
            print("このログファイルにはエラー出力はありません。")

if __name__ == "__main__":
    check_all_error_logs()