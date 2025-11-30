# Phase 3-2: レース詳細取得 - 実行手順書

**作成日**: 2025/11/30  
**ステータス**: 準備完了 ✅

---

## 📦 必要なファイル

以下のファイルがすべて揃っていることを確認してください：

```
/home/claude/
├── keiba.db                      ✅ データベース
├── race_detail_scraper.py        ✅ スクレイパー本体
├── batch_race_detail.py          ✅ バッチ処理スクリプト
├── check_race_progress.py        ✅ 進捗確認スクリプト
└── PHASE3-2_EXECUTION_GUIDE.md   ✅ このファイル
```

---

## 🎯 現在の状況

```
総レース数: 997件
詳細未取得: 997件（100%）
重賞レース: 129件（G1:42, G2:32, G3:55）
```

**取得予定の情報**:
- venue（競馬場）: 東京、京都、中山など
- track_type（コース種別）: 芝、ダート
- distance（距離）: 1200m、1600m、2000mなど
- track_condition（馬場状態）: 良、稍重、重、不良
- horse_count（出走頭数）

---

## 🚀 実行手順

### ステップ0: 環境準備

```bash
# プロジェクトディレクトリに移動
cd ~/デスクトップ/repo/keiba-yosoka-ai

# 仮想環境の有効化
source venv/Scripts/activate  # Git Bash
# または
venv\Scripts\activate  # Windows CMD

# 必要なファイルをコピー
# Claudeからダウンロードした以下のファイルをプロジェクトルートに配置:
# - race_detail_scraper.py
# - batch_race_detail.py
# - check_race_progress.py
# - keiba.db（最新版）
```

---

### ステップ1: 進捗確認

```bash
python check_race_progress.py
```

**期待される出力**:
```
============================================================
レース詳細取得 進捗レポート
============================================================

【全体】
総レース数: 997件
詳細取得済み: 0件 (0.0%)
詳細未取得: 997件

進捗: [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.0%

【重賞】
重賞レース数: 129件
詳細取得済み: 0件 (0.0%)
詳細未取得: 129件
```

---

### ステップ2: テスト実行（1件のみ）

まず1件だけ取得して、動作を確認します。

```bash
python batch_race_detail.py --limit 1
```

**期待される動作**:
1. ChromeDriverが起動（ヘッドレスモード）
2. netkeibaにアクセス
3. レース詳細を取得
4. DBを更新
5. "✅ Successfully updated race_id=..." と表示

**所要時間**: 約10-15秒

---

### ステップ3: 小規模バッチ実行（10件）

```bash
python batch_race_detail.py --limit 10
```

**所要時間**: 約1-2分

進捗確認:
```bash
python check_race_progress.py
```

→ `詳細取得済み: 10件 (1.0%)` と表示されればOK

---

### ステップ4: 本番実行

#### プランA: 100件ずつ実行（推奨・安全）

```bash
# 1回目: 0-99件
python batch_race_detail.py --limit 100 --offset 0

# 進捗確認
python check_race_progress.py

# 2回目: 100-199件
python batch_race_detail.py --limit 100 --offset 100

# 進捗確認
python check_race_progress.py

# 3回目: 200-299件
python batch_race_detail.py --limit 100 --offset 200

# ... 10回繰り返し
```

**所要時間**: 約5-7分/100件 × 10回 = 約50-70分

---

#### プランB: 重賞優先実行

まず重賞だけ取得して早期分析を可能にします。

```bash
# 重賞のみ取得（129件）
python batch_race_detail.py --grade-only

# 進捗確認（重賞のみ）
python check_race_progress.py --grade-only

# 残りの一般レース（868件）
python batch_race_detail.py
```

**所要時間**: 
- 重賞: 約10-15分
- 残り: 約45-60分

---

#### プランC: 全件一括実行（簡単だが長時間）

```bash
# 全997件を一括取得
python batch_race_detail.py

# 進捗監視（別ターミナルで）
watch -n 60 python check_race_progress.py
```

**所要時間**: 約50-70分（連続実行）

---

#### プランD: 自動化スクリプト（Git Bash）

```bash
#!/bin/bash
# batch_all_races.sh

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

# 残り（900-996件）
python batch_race_detail.py --limit 100 --offset 900

echo "全件完了！"
python check_race_progress.py --verbose
```

実行:
```bash
chmod +x batch_all_races.sh
./batch_all_races.sh
```

---

## 📊 実行中の監視

### リアルタイム進捗確認

```bash
# 別のターミナルを開いて
watch -n 30 python check_race_progress.py
```

### ログ確認

```bash
# 最新のログファイル
ls -lt logs/batch_race_detail_*.log | head -1

# ログをリアルタイム表示
tail -f logs/batch_race_detail_*.log

# エラーのみ抽出
grep "ERROR" logs/batch_race_detail_*.log
grep "❌" logs/batch_race_detail_*.log

# 成功件数をカウント
grep "✅" logs/batch_race_detail_*.log | wc -l
```

---

## ✅ 完了確認

### 全件取得完了の確認

```bash
python check_race_progress.py --verbose
```

**期待される出力**:
```
【全体】
総レース数: 997件
詳細取得済み: 997件 (100.0%)
詳細未取得: 0件

進捗: [████████████████████████████████████████] 100.0%

【重賞】
重賞レース数: 129件
詳細取得済み: 129件 (100.0%)
詳細未取得: 0件

進捗: [████████████████████████████████████████] 100.0%

【グレード別】
G1: 42/42件 (100.0%) - 残り0件
G2: 32/32件 (100.0%) - 残り0件
G3: 55/55件 (100.0%) - 残り0件

【コース別】（取得済みのみ）
芝: XXX件
ダート: XXX件

【競馬場別】（取得済みのみ）
東京: XXX件
京都: XXX件
中山: XXX件
...
```

---

### データ品質確認

```bash
python << 'EOF'
import sqlite3

conn = sqlite3.connect('keiba.db')
cursor = conn.cursor()

print("=" * 60)
print("データ品質レポート")
print("=" * 60)

# 基本統計
cursor.execute("SELECT COUNT(*) FROM races")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM races WHERE track_type IS NOT NULL AND track_type != '不明'")
has_track = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM races WHERE distance > 0")
has_distance = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM races WHERE venue IS NOT NULL AND venue != '不明'")
has_venue = cursor.fetchone()[0]

print(f"総レース数: {total}件")
print(f"コース種別あり: {has_track}件 ({has_track/total*100:.1f}%)")
print(f"距離情報あり: {has_distance}件 ({has_distance/total*100:.1f}%)")
print(f"競馬場情報あり: {has_venue}件 ({has_venue/total*100:.1f}%)")

# コース種別の分布
print("\nコース種別:")
cursor.execute("SELECT track_type, COUNT(*) FROM races WHERE track_type != '不明' GROUP BY track_type")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}件")

# 距離の分布（上位10件）
print("\n距離（上位10）:")
cursor.execute("SELECT distance, COUNT(*) FROM races WHERE distance > 0 GROUP BY distance ORDER BY COUNT(*) DESC LIMIT 10")
for row in cursor.fetchall():
    print(f"  {row[0]}m: {row[1]}件")

# 競馬場の分布
print("\n競馬場:")
cursor.execute("SELECT venue, COUNT(*) FROM races WHERE venue != '不明' GROUP BY venue ORDER BY COUNT(*) DESC")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}件")

conn.close()
EOF
```

---

## 🚨 トラブルシューティング

### Q: ChromeDriverエラーが発生

```bash
# Chromeプロセスを全て終了
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T

# スクリプトを再実行
python batch_race_detail.py --limit 100 --offset [前回の続き]
```

---

### Q: 途中で止まった

```bash
# 現在の進捗を確認
python check_race_progress.py

# 出力例: 詳細取得済み: 345件

# 続きから実行
python batch_race_detail.py --limit 100 --offset 345
```

---

### Q: エラーレートが高い（10%以上失敗）

```bash
# 待機時間を増やす
python batch_race_detail.py --limit 50 --sleep 5

# または重賞のみ先に取得
python batch_race_detail.py --grade-only --sleep 5
```

---

### Q: データベースがロックされている

```bash
# 他のスクリプトやDB接続を全て閉じる
# SQLite Browserなどが開いていないか確認

# スクリプトを再実行
```

---

## 📈 次のステップ（Phase 4）

Phase 3-2完了後、以下に進みます：

### 1. データ分析の準備

```bash
# 分析用のスクリプトを作成
# - 的中率の計算
# - 回収率（ROI）の計算
# - 予想家ランキング生成
```

### 2. 重賞特化分析

```bash
# 重賞レースでの成績を集計
# - G1での的中率
# - G2/G3での回収率
# - コース別（芝/ダート）の得意不得意
```

### 3. 予想家プロファイリング

```bash
# 各予想家の特徴分析
# - 得意な距離
# - 得意な競馬場
# - 得意なコース種別
```

---

## 📝 実行ログの記録

実行時は以下の情報を記録してください：

```
日時: 2025/11/30
実行プラン: [A/B/C/D]
開始時刻: HH:MM
終了時刻: HH:MM
処理件数: XXX件
成功: XXX件
失敗: XXX件
エラー内容: [あれば記載]
```

---

## 🎉 完了チェックリスト

- [ ] 全997件のレース詳細取得完了
- [ ] エラー率 < 5%
- [ ] 芝/ダート情報が正しく取得されている
- [ ] 競馬場情報が正しく取得されている
- [ ] 距離情報が正しく取得されている
- [ ] データベースバックアップを取得
- [ ] ログファイルを保存
- [ ] CURRENT_STATUS.mdを更新
- [ ] GitHubにコミット

---

**次回チャットでの再開時**:
1. このファイル（PHASE3-2_EXECUTION_GUIDE.md）をアップロード
2. `python check_race_progress.py`で進捗確認
3. 続きから実行

Good luck! 🏇
