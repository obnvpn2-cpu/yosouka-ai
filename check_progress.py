import sqlite3
import re

# ログファイルから最後に処理したインデックスを取得
def get_last_processed_index():
    """最新のログファイルから最後に処理したインデックスを取得"""
    import glob
    import os
    
    log_files = glob.glob('logs/scraper_*.log')
    if not log_files:
        return None
    
    # 最新のログファイルを取得
    latest_log = max(log_files, key=os.path.getmtime)
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            content = f.read()
            # "Processed X predictors (from index Y to Z)" を探す
            matches = re.findall(r'Processed \d+ predictors \(from index (\d+) to (\d+)\)', content)
            if matches:
                # 最後のマッチを取得
                last_match = matches[-1]
                start_idx = int(last_match[0])
                end_idx = int(last_match[1])
                return end_idx
    except Exception as e:
        print(f"ログ読み込みエラー: {e}")
    
    return None

# データベース接続
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

print("=" * 70)
print("現在の進捗状況")
print("=" * 70)

# 基本統計
cursor.execute("SELECT COUNT(*) FROM predictors")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
successful = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM predictions")
total_predictions = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) 
    FROM predictions p 
    JOIN races r ON p.race_id = r.id
    WHERE r.grade IS NOT NULL
""")
grade_predictions = cursor.fetchone()[0]

print(f"\n【データベース統計】")
print(f"登録予想家: {total}人")
print(f"成功（データあり）: {successful}人 ({successful/total*100:.1f}%)")
print(f"失敗（データなし）: {total - successful}人 ({(total-successful)/total*100:.1f}%)")
print(f"総予想数: {total_predictions}件")
print(f"重賞予想: {grade_predictions}件")

# ログから最後の処理インデックスを取得
last_index = get_last_processed_index()

print(f"\n" + "=" * 70)
print("次の実行コマンド")
print("=" * 70)

if last_index is not None:
    next_offset = last_index + 1
    print(f"\n✅ 最後の処理: index {last_index}まで")
    print(f"✅ 次のoffset: {next_offset}")
    print(f"\n推奨コマンド:")
    print(f"python backend/scraper/main.py --limit 10 --offset {next_offset}")
    
    remaining = total - next_offset
    if remaining > 0:
        runs_needed = (remaining + 9) // 10
        print(f"\n残り: {remaining}人")
        print(f"推定: あと{runs_needed}回の実行で完了")
    else:
        print(f"\n🎉 全予想家の処理が完了しました！")
        print(f"\n次のステップ:")
        print(f"1. 失敗した予想家のリトライ")
        print(f"2. データ品質の検証")
        print(f"3. Phase 4（分析機能）への移行")
else:
    print(f"\n⚠️ ログファイルが見つかりません")
    print(f"\n代替案（成功数ベース）:")
    print(f"python backend/scraper/main.py --limit 10 --offset {successful}")
    print(f"\n注意: この方法だと一部の予想家を重複処理する可能性があります")

print("=" * 70)

conn.close()
