# main.py 修正内容

## 🐛 問題点

**`--limit`と`--offset`オプションが実装されていませんでした！**

### 現象
```bash
# このコマンドを実行しても...
python backend/scraper/main.py --limit 10 --offset 49

# 実際には offset が無視され、最初（offset 0）から処理を試みる
# → 既存データは重複チェックでスキップ
# → 新しいデータが追加されない
# → offset 49 のまま進まない
```

---

## ✅ 修正内容

### 1. argparseの追加

**修正前:**
```python
# テスト用：最初の5人のみ処理
test_mode = "--test" in sys.argv
limit = 5 if test_mode else len(predictors)
```

**修正後:**
```python
# 引数パーサーを設定
parser = argparse.ArgumentParser(description='競馬予想家スクレイピング')
parser.add_argument('--limit', type=int, default=None, help='処理する予想家の数')
parser.add_argument('--offset', type=int, default=0, help='開始位置（スキップする予想家の数）')
parser.add_argument('--test', action='store_true', help='テストモード（最初の5人のみ）')

args = parser.parse_args()
```

### 2. offset/limit の適用

**修正前:**
```python
for i, predictor_data in enumerate(predictors[:limit], 1):
    # 常に最初から処理
```

**修正後:**
```python
# 処理範囲を決定
if args.test:
    start_idx = 0
    end_idx = min(5, len(predictors))
else:
    start_idx = args.offset
    if args.limit:
        end_idx = min(start_idx + args.limit, len(predictors))
    else:
        end_idx = len(predictors)

target_predictors = predictors[start_idx:end_idx]

for i, predictor_data in enumerate(target_predictors, 1):
    # offset を考慮して処理
```

### 3. ログ出力の改善

**追加:**
```python
logger.info(f"Arguments: limit={args.limit}, offset={args.offset}, test={args.test}")
logger.info(f"Processing predictors {start_idx+1} to {end_idx} ({total_count} predictors)")
```

---

## 📦 適用方法

### ステップ1: ファイルを置き換え

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai

# バックアップを作成
cp backend/scraper/main.py backend/scraper/main.py.backup

# 修正版を適用
cp ~/Downloads/main.py backend/scraper/main.py
```

### ステップ2: 動作確認

```bash
# テスト実行（1人だけ、offset 49から）
python backend/scraper/main.py --limit 1 --offset 49

# ログを確認
tail -50 logs/scraper_*.log
```

ログに以下のように表示されればOK:
```
Arguments: limit=1, offset=49, test=False
Processing predictors 50 to 50 (1 predictors)
[1/1] Processing predictor: ○○○ (ID: XXX)
```

### ステップ3: 本実行

```bash
# 50-59人目を処理
python backend/scraper/main.py --limit 10 --offset 49
```

---

## 🎯 使用例

```bash
# 最初の10人
python backend/scraper/main.py --limit 10 --offset 0

# 50-59人目
python backend/scraper/main.py --limit 10 --offset 49

# 100人目から最後まで
python backend/scraper/main.py --offset 99

# テストモード（最初の5人のみ）
python backend/scraper/main.py --test
```

---

## 📊 進捗確認コマンド

```bash
python << 'EOF'
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
processed = cursor.fetchone()[0]

print(f"処理済み: {processed}/186人 ({processed/186*100:.1f}%)")
print(f"次のコマンド: python backend/scraper/main.py --limit 10 --offset {processed}")

conn.close()
EOF
```

---

## 🔍 トラブルシューティング

### Q: 実行しても進まない
A: ログを確認してください
```bash
tail -100 logs/scraper_*.log | grep "Processing predictors"
```

正しく動作していれば:
```
Processing predictors 50 to 60 (10 predictors)
```

間違っている場合:
```
Processing predictors 1 to 10 (10 predictors)  # offset が無視されている
```

### Q: 引数が認識されない
A: `argparse`がインポートされているか確認
```bash
python -c "import argparse; print('OK')"
```

---

これで`--offset`が正しく動作します！
