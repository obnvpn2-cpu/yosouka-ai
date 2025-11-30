# Phase 3-2: レース詳細取得 実行ガイド

**作成日**: 2025/11/30  
**対象**: 997件のレース詳細情報取得

---

## 📋 概要

Phase 3-1で取得したrace_idを使って、各レースの詳細情報を取得します。

**取得する情報**:
- レース開催日（race_date）
- 競馬場（track）
- コース種別（course_type: 芝/ダート）
- 距離（distance）
- クラス（class）

---

## 🎯 現在の状況

```
総レース数: 997件
詳細未取得: 997件（100%）
重賞レース: 1,619件中の一部が含まれる
```

---

## 🚀 実行手順

### 1. 進捗確認

まず現在の状況を確認します。

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai
python check_race_progress.py
```

詳細表示:
```bash
python check_race_progress.py --verbose
```

---

### 2. バッチ処理実行

#### 🟢 推奨: 100件ずつ実行（安全・確実）

```bash
# 最初の100件
python batch_race_detail.py --limit 100

# 進捗確認
python check_race_progress.py

# 次の100件
python batch_race_detail.py --limit 100 --offset 100

# さらに次の100件
python batch_race_detail.py --limit 100 --offset 200
```

**所要時間**: 約5-7分/100件（待機3秒の場合）

---

#### 🟡 中級: 重賞優先取得

重賞レースを優先的に取得する場合:

```bash
# 重賞のみ取得
python batch_race_detail.py --grade-only

# 進捗確認（重賞のみ）
python check_race_progress.py --grade-only
```

---

#### 🔴 上級: 全件一括取得（時間がかかる）

```bash
# 全997件を一括取得
python batch_race_detail.py

# 推定所要時間: 約50-70分
```

---

### 3. 自動化スクリプト（オプション）

#### Windows（Git Bash / MINGW64）

```bash
# 100件ずつ自動実行
for i in {0..900..100}; do
  echo "========================================="
  echo "処理中: offset $i"
  echo "========================================="
  python batch_race_detail.py --limit 100 --offset $i
  
  # 進捗確認
  python check_race_progress.py
  
  # バッチ間の待機（10秒）
  sleep 10
done
```

---

## 🎛️ オプション設定

### 待機時間の調整

アクセス頻度を下げたい場合:

```bash
# 待機時間を5秒に設定
python batch_race_detail.py --limit 100 --sleep 5
```

### データベースパスの指定

デフォルト以外の場所にDBがある場合:

```bash
python batch_race_detail.py --db /path/to/keiba.db
```

---

## 📊 進捗管理

### バッチ実行の推奨間隔

```
1回目:   0-99件    (--limit 100 --offset 0)
  ↓ 5分待機
2回目: 100-199件   (--limit 100 --offset 100)
  ↓ 5分待機
3回目: 200-299件   (--limit 100 --offset 200)
  ...
10回目: 900-997件  (--limit 100 --offset 900)
```

**総所要時間**: 約1-1.5時間（待機時間含む）

---

## 🔍 エラー対処

### よくあるエラー

#### 1. ChromeDriverエラー

```bash
# Chromeプロセスを強制終了
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T

# スクリプト再実行
python batch_race_detail.py --limit 100 --offset [前回の続き]
```

#### 2. ネットワークエラー

```bash
# 待機時間を増やして再試行
python batch_race_detail.py --limit 50 --offset [前回の続き] --sleep 5
```

#### 3. データベースロックエラー

```bash
# 他のスクリプトが動いていないか確認
# スクリプトを再実行
```

---

## 📈 進捗の見方

### check_race_progress.pyの出力例

```
============================================================
レース詳細取得 進捗レポート
============================================================

【全体】
総レース数: 997件
詳細取得済み: 345件 (34.6%)
詳細未取得: 652件

進捗: [█████████████░░░░░░░░░░░░░░░] 34.6%

【重賞】
重賞レース数: 150件
詳細取得済み: 52件 (34.7%)
詳細未取得: 98件

進捗: [█████████████░░░░░░░░░░░░░░░] 34.7%
============================================================

【次に実行すべきコマンド】

# 次の100件を取得（推奨）
python batch_race_detail.py --limit 100 --offset 345

# 重賞のみ50件取得
python batch_race_detail.py --limit 50 --offset 52 --grade-only

# 全件取得（残り652件）
python batch_race_detail.py --offset 345
```

---

## ✅ 完了確認

全レース取得完了後:

```bash
python check_race_progress.py --verbose
```

以下が表示されればOK:

```
詳細取得済み: 997件 (100.0%)
詳細未取得: 0件

進捗: [████████████████████████████████████████] 100.0%
```

---

## 📝 取得データの確認

### SQLで確認

```bash
sqlite3 data/keiba.db
```

```sql
-- レース詳細の確認
SELECT 
    race_name,
    race_date,
    track,
    course_type,
    distance,
    grade
FROM races
WHERE course_type IS NOT NULL
LIMIT 10;

-- コース種別の分布
SELECT course_type, COUNT(*) 
FROM races 
WHERE course_type IS NOT NULL
GROUP BY course_type;

-- 競馬場別の件数
SELECT track, COUNT(*) 
FROM races 
WHERE track IS NOT NULL
GROUP BY track
ORDER BY COUNT(*) DESC;
```

### Pythonで確認

```python
import sqlite3

conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

# 芝とダートの件数
cursor.execute("""
    SELECT course_type, COUNT(*) 
    FROM races 
    WHERE course_type IS NOT NULL
    GROUP BY course_type
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}件")

# 距離の分布
cursor.execute("""
    SELECT distance, COUNT(*) 
    FROM races 
    WHERE distance IS NOT NULL
    GROUP BY distance
    ORDER BY distance
""")
print("\n距離別:")
for row in cursor.fetchall():
    print(f"{row[0]}m: {row[1]}件")

conn.close()
```

---

## 🔄 次のフェーズ

Phase 3-2完了後:

1. **Phase 4: データ分析**
   - 的中率・回収率の計算
   - 予想家ランキング生成
   - 重賞特化予想家の特定

2. **データ品質検証**
   - 欠損値チェック
   - 異常値検出
   - データ整合性確認

---

## 💡 Tips

### 効率的な実行方法

1. **重賞を優先**: まず重賞だけ取得して分析開始
2. **並行処理**: 複数のターミナルで異なるoffsetを実行（注意: アクセス制限に注意）
3. **時間分散**: 朝・昼・夜に分けて実行

### ログの活用

```bash
# 最新のログを確認
tail -f logs/batch_race_detail_*.log

# エラーのみ抽出
grep "ERROR" logs/batch_race_detail_*.log

# 成功件数をカウント
grep "✅ 成功" logs/batch_race_detail_*.log | wc -l
```

---

## 🚨 注意事項

1. **アクセス頻度**
   - 待機時間は最低3秒推奨
   - 短時間での大量アクセスはIP制限の可能性

2. **データベースバックアップ**
   - 定期的にバックアップを取る
   ```bash
   cp data/keiba.db data/keiba.db.backup_$(date +%Y%m%d_%H%M%S)
   ```

3. **中断・再開**
   - 中断しても `--offset` で続きから実行可能
   - 進捗は自動保存される

---

## 📞 トラブル時の対処

問題が発生した場合:

1. ログファイルを確認
2. `check_race_progress.py` で現在の状況を確認
3. エラーメッセージを記録
4. 必要に応じてGitHubでIssueを作成

---

**作成者**: Claude  
**最終更新**: 2025/11/30
