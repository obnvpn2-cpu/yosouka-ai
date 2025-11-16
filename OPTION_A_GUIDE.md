# Seleniumでのデータ取得完了ガイド（選択肢A）

## 📋 概要

このガイドでは、Seleniumの改善版を使用して残りのデータを取得し、その後Playwrightに移行する手順を説明します。

---

## 🔧 ステップ1: 改善版の適用

### 1-1. 最新版prediction.pyの適用

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai

# バックアップ
cp backend/scraper/prediction.py backend/scraper/prediction.py.backup

# 最新版を適用
cp ~/Downloads/prediction_final.py backend/scraper/prediction.py
```

### 1-2. main.pyの待機時間を延長

`backend/scraper/main.py` を編集：

**変更前**:
```python
time.sleep(15)  # Wait before next predictor
```

**変更後**:
```python
time.sleep(30)  # Wait before next predictor (doubled for stability)
```

---

## 📊 ステップ2: 現在の進捗確認

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai
export PYTHONPATH=$(pwd)

python << 'EOF'
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

print("=" * 60)
print("現在の進捗")
print("=" * 60)

# 処理済み予想家
cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
processed = cursor.fetchone()[0]

# 総予想数
cursor.execute("SELECT COUNT(*) FROM predictions")
total_predictions = cursor.fetchone()[0]

# 重賞予想数
cursor.execute("""
    SELECT COUNT(*) 
    FROM predictions p 
    JOIN races r ON p.race_id = r.id 
    WHERE r.grade IS NOT NULL
""")
grade_predictions = cursor.fetchone()[0]

print(f"\n処理済み予想家: {processed}/186人 ({processed/186*100:.1f}%)")
print(f"総予想数: {total_predictions}件")
print(f"重賞予想数: {grade_predictions}件")
print(f"\n残り: {186 - processed}人")

# 次のoffset
print(f"\n次の実行:")
print(f"python backend/scraper/main.py --limit 10 --offset {processed}")

conn.close()
print("\n" + "=" * 60)
EOF
```

---

## 🚀 ステップ3: データ取得の実行

### 推奨実行スケジュール

残り約156人を10人ずつ実行する場合、約16回の実行が必要です。

**各実行後は必ず30分〜1時間休憩してください**（Netkeibaの制限回避）

```bash
export PYTHONPATH=$(pwd)

# === 実行1回目 ===
python backend/scraper/main.py --limit 10 --offset 30
# 30分休憩

# === 実行2回目 ===
python backend/scraper/main.py --limit 10 --offset 40
# 30分休憩

# ... 以降同様
```

### より安全な5人ずつ実行

```bash
# === 実行1回目 ===
python backend/scraper/main.py --limit 5 --offset 30
# 30分休憩

# === 実行2回目 ===
python backend/scraper/main.py --limit 5 --offset 35
# 30分休憩

# ... 以降同様
```

---

## 📝 ステップ4: 失敗した予想家の記録

各実行後、失敗した予想家を`FAILED_PREDICTORS.md`に記録してください：

```markdown
### 実行日: YYYY/MM/DD - X回目（offset XX-XX）

| 予想家名 | ID | エラー内容 | 備考 |
|---------|-----|----------|------|
| 予想家名 | XXX | エラー内容 | |

**成功率**: X/10人 = XX%
```

---

## ⚠️ トラブルシューティング

### エラーが3回連続で発生した場合

**即座に停止して1時間以上休憩**

```bash
# Chrome/ChromeDriverを完全終了
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T

# システムを再起動（推奨）
```

### 成功率が50%を下回った場合

**その日の実行を終了し、翌日再開**

Netkeibaがあなたのアクセスパターンをボットと判断している可能性があります。

---

## ✅ ステップ5: 完了確認

全データ取得完了後：

```bash
python << 'EOF'
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

print("=" * 60)
print("最終集計")
print("=" * 60)

# 処理済み予想家
cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
processed = cursor.fetchone()[0]

# 総予想数
cursor.execute("SELECT COUNT(*) FROM predictions")
total_predictions = cursor.fetchone()[0]

# 重賞予想数
cursor.execute("""
    SELECT COUNT(*) 
    FROM predictions p 
    JOIN races r ON p.race_id = r.id 
    WHERE r.grade IS NOT NULL
""")
grade_predictions = cursor.fetchone()[0]

# 高信頼度予想家
cursor.execute("SELECT COUNT(*) FROM predictors WHERE data_reliability = 'high'")
high_reliability = cursor.fetchone()[0]

# 的中データ
cursor.execute("""
    SELECT COUNT(*) 
    FROM predictions 
    WHERE is_hit = 1 AND payout > 0
""")
hit_with_payout = cursor.fetchone()[0]

print(f"\n✅ 処理済み予想家: {processed}/186人 ({processed/186*100:.1f}%)")
print(f"✅ 総予想数: {total_predictions}件")
print(f"✅ 重賞予想数: {grade_predictions}件")
print(f"✅ 高信頼度予想家: {high_reliability}人")
print(f"✅ 的中+配当データ: {hit_with_payout}件")

if processed < 186:
    print(f"\n⚠️  未処理: {186 - processed}人")
    print("失敗した予想家のリトライが必要です")
else:
    print("\n🎉 全予想家のデータ取得完了！")

conn.close()
print("\n" + "=" * 60)
EOF
```

---

## 🔄 ステップ6: 失敗した予想家のリトライ

`FAILED_PREDICTORS.md`を参照して、失敗した予想家を個別にリトライ：

```bash
# 例: 翔天 (ID: 670)
python backend/scraper/main.py --limit 1 --offset 16

# 各リトライ間に15分以上待機
```

---

## 📊 データ品質チェック

全データ取得完了後、品質を確認：

```bash
python << 'EOF'
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/keiba.db')

# 予想家ごとの統計
df_predictors = pd.read_sql_query("""
    SELECT 
        name,
        total_predictions,
        grade_race_predictions,
        data_reliability
    FROM predictors
    WHERE total_predictions > 0
    ORDER BY grade_race_predictions DESC
    LIMIT 20
""", conn)

print("トップ20予想家（重賞予想数順）:")
print(df_predictors.to_string(index=False))

# グレード別統計
df_grades = pd.read_sql_query("""
    SELECT 
        r.grade,
        COUNT(*) as count,
        COUNT(CASE WHEN p.is_hit = 1 THEN 1 END) as hits,
        ROUND(AVG(CASE WHEN p.payout > 0 THEN p.payout END), 0) as avg_payout
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    WHERE r.grade IS NOT NULL
    GROUP BY r.grade
    ORDER BY r.grade
""", conn)

print("\n\nグレード別統計:")
print(df_grades.to_string(index=False))

conn.close()
EOF
```

---

## 🎯 Phase 4への移行準備

データ取得完了後、以下を確認：

- [ ] 全186人のデータ取得完了
- [ ] FAILED_PREDICTORS.mdの更新完了
- [ ] データ品質チェック完了
- [ ] GitHubにコミット&プッシュ完了

**次のステップ**: Playwrightへの移行（別途ガイド作成予定）

---

## 📅 推定スケジュール

| タスク | 所要時間 | 備考 |
|--------|----------|------|
| 残り156人の取得（10人ずつ） | 16回実行 × 20分 = 約5-6時間 | 休憩含む |
| 失敗予想家のリトライ | 約10人 × 5分 = 50分 | |
| データ品質チェック | 30分 | |
| **合計** | **約7-8時間** | 数日に分散推奨 |

---

## ⚠️ 重要な注意事項

1. **一度に大量実行しない**: 10人以上連続実行は避ける
2. **休憩を取る**: 各実行後30分〜1時間休憩
3. **時間帯を分散**: 朝・昼・夜で分けて実行
4. **エラー発生時**: 即座に停止し、翌日再開
5. **IP制限**: 24時間制限が発動したら、その日は中止

---

これで選択肢Aの準備が完了です！慎重に、計画的にデータ取得を進めてください。🚀
