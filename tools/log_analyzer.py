import re
from datetime import datetime
import glob
import os

def analyze_log_file(file_path: str) -> dict:
    """ログファイルを解析してエラーと実行時間を確認する
    
    Args:
        file_path: ログファイルのパス
    
    Returns:
        dict: 解析結果
    """
    errors = []
    executions = []
    start_time = None
    
    with open(file_path, 'r') as f:
        for line in f:
            # タイムスタンプとメッセージを抽出
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .*? - (INFO|ERROR|WARNING) - (.*)', line)
            if match:
                timestamp_str, level, message = match.groups()
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                
                # エラーを検出
                if level == 'ERROR':
                    errors.append({
                        'timestamp': timestamp,
                        'message': message
                    })
                
                # 実行時間を計算
                if 'start: hourly_10_update_scheduler' in message:
                    start_time = timestamp
                elif 'end: hourly_10_update_scheduler' in message and start_time:
                    duration = (timestamp - start_time).total_seconds()
                    executions.append({
                        'start': start_time,
                        'end': timestamp,
                        'duration': duration
                    })
                    start_time = None
    
    # 異常な実行時間を検出（例：2分以上）
    long_executions = [
        exec for exec in executions 
        if exec['duration'] > 120  # 2分以上を異常とみなす
    ]
    
    return {
        'errors': errors,
        'long_executions': long_executions,
        'total_executions': len(executions)
    }

def check_logs(log_dir: str = 'logs') -> None:
    """ログディレクトリ内の全ログファイルをチェック"""
    log_files = glob.glob(os.path.join(log_dir, '*__main__.log'))
    
    for log_file in log_files:
        print(f"\nAnalyzing {log_file}...")
        result = analyze_log_file(log_file)
        
        # 結果を表示
        if result['errors']:
            print("\nエラーが検出されました:")
            for error in result['errors']:
                print(f"- {error['timestamp']}: {error['message']}")
        
        if result['long_executions']:
            print("\n実行時間が長い処理が検出されました:")
            for exec in result['long_executions']:
                print(f"- 開始: {exec['start']}")
                print(f"  終了: {exec['end']}")
                print(f"  所要時間: {exec['duration']:.1f}秒")
        
        if not (result['errors'] or result['long_executions']):
            print("問題は検出されませんでした")
        
        print(f"\n総実行回数: {result['total_executions']}")

if __name__ == "__main__":
    check_logs()