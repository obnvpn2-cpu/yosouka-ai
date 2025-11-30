# 🏇 競馬予想家分析AI

netkeiba掲載の予想家の過去成績を分析し、重賞レースにおける的中率・回収率が高い予想家を推薦するシステム

---

## 📊 プロジェクト現状（2025/11/30 22:00）

- **進捗**: Phase 3-2（レース詳細取得）開始 - 4%完了
- **予想家データ**: 187/186人完了（100%）✅
- **有効予想数**: 9,262件 ✅
- **重賞予想数**: 1,619件 ✅
- **race_id更新**: 完了（99.3%）✅
- **レース詳細情報**: 40/997件（4%）🔄

詳細は [CURRENT_STATUS.md](CURRENT_STATUS.md) を参照

---

## 🎯 プロジェクト概要

### 目的
重賞レースで信頼できる予想家を推薦するシステムの構築

### データソース
- netkeiba.com（予想家の過去予想データ）
- 予想家187人、予想9,262件を収集済み

### 主な機能（実装予定）
1. 予想家の過去成績分析
2. 重賞レースでの的中率・回収率計算
3. レース条件に基づく予想家推薦
4. Web UIでのデータ可視化

---

## 🛠️ 技術スタック

### バックエンド
- **言語**: Python 3.12+
- **スクレイピング**: Selenium, loguru
- **データベース**: SQLite（開発）/ PostgreSQL（本番予定）
- **分析**: pandas, numpy
- **API**: FastAPI（Phase 5で実装予定）

### フロントエンド（Phase 6で実装予定）
- React + TypeScript
- Material-UI
- Recharts

---

## 📁 プロジェクト構造

```
keiba-yosoka-ai/
├── backend/
│   ├── scraper/
│   │   ├── main.py                          ✅ 予想家データ取得
│   │   ├── prediction.py                    ✅ 予想履歴取得
│   │   ├── update_race_ids_v2.py            ✅ race_id更新
│   │   ├── batch_update_race_ids_v2.py      ✅ 一括更新
│   │   ├── race_detail_scraper.py           ✅ レース詳細取得（テスト用）
│   │   └── race_detail_scraper_with_db.py   ⭐ レース詳細取得（DB更新）
│   ├── models/
│   │   └── database.py                      # データベースモデル
│   └── database.py                          # DB接続
├── data/
│   ├── keiba.db                             ⭐ データベース
│   └── race_details/                        ⭐ レース詳細JSON
├── logs/                                    ⭐ 実行ログ
├── batch_race_detail.py                     ⭐ バッチ処理スクリプト
├── check_race_progress.py                   ⭐ 進捗確認スクリプト
├── drivers/
│   └── chromedriver.exe                     # Selenium用
├── venv/                                    # Python仮想環境
├── .env                                     # 環境変数（認証情報）
├── README.md                                # このファイル
├── CURRENT_STATUS.md                        ⭐ 詳細な現在状況
├── PROJECT_SUMMARY.md                       ⭐ プロジェクトサマリー
└── 新しいチャットでの再開ガイド.md           # 新チャット再開手順
```

---

## 🚀 クイックスタート

### 初回セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/obnvpn2-cpu/yosouka-ai.git
cd keiba-yosoka-ai

# 2. 仮想環境作成
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash

# 3. パッケージインストール
pip install -r requirements.txt
pip install loguru  # 追加で必要

# 4. 環境変数設定
cp .env.example .env
# .envを編集してnetkeiba認証情報を設定（オプション）

# 5. データベース初期化
python backend/init_db.py
```

### 現在の進捗確認

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai
python check_race_progress.py
```

**出力例**:
```
============================================================
レース詳細取得 進捗レポート
============================================================

【全体】
総レース数: 997件
詳細取得済み: 40件 (4.0%)
詳細未取得: 957件

進捗: [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 4.0%
```

---

## 📈 開発フェーズ

- [x] **Phase 1**: プロジェクトセットアップ ✅
- [x] **Phase 2**: 予想家データ取得（187人完了）✅
- [x] **Phase 3-1**: race_id更新（99.3%完了）✅
- [ ] **Phase 3-2**: レース詳細情報取得（4%完了）🔄 **← 現在ここ**
- [ ] **Phase 4**: 分析機能実装 ⏳
- [ ] **Phase 5**: API実装 ⏳
- [ ] **Phase 6**: フロントエンド実装 ⏳
- [ ] **Phase 7**: デプロイ ⏳

### 現在のフェーズ詳細（Phase 3-2）

**目的**: 997件のレースについて詳細情報を取得

**取得する情報**:
- **venue**（競馬場）: 東京、京都、中山など
- **track_type**（コース種別）: 芝、ダート
- **distance**（距離）: 1200m、1600m、2000mなど
- **track_condition**（馬場状態）: 良、稍重、重、不良
- **horse_count**（出走頭数）

**使用スクリプト**:
- `race_detail_scraper_with_db.py` - スクレイパー本体（DB更新機能付き）
- `batch_race_detail.py` - バッチ処理
- `check_race_progress.py` - 進捗確認

**実行方法**:
```bash
# 100件ずつ処理（推奨）
python batch_race_detail.py --limit 100

# 進捗確認
python check_race_progress.py

# 全件処理
python batch_race_detail.py
```

**推定所要時間**:
- 100件: 約40分
- 全件（997件）: 約6-7時間

---

## 💾 データベース構造

### 主要テーブル

#### Predictors（予想家）- 187人
```sql
- id: INTEGER PRIMARY KEY
- netkeiba_id: INTEGER UNIQUE
- name: TEXT
- total_predictions: INTEGER
- grade_race_predictions: INTEGER
- data_reliability: TEXT (low/medium/high)
```

#### Predictions（予想）- 9,262件（有効）
```sql
- id: INTEGER PRIMARY KEY
- predictor_id: INTEGER (FK)
- race_id: INTEGER (FK)
- netkeiba_prediction_id: INTEGER
- is_hit: BOOLEAN
- payout: INTEGER
- roi: FLOAT
```

#### Races（レース）- 997件
```sql
- id: INTEGER PRIMARY KEY
- race_id: TEXT UNIQUE（12桁）
- race_name: TEXT
- race_date: DATETIME
- venue: TEXT ⭐ Phase 3-2で取得中
- grade: TEXT (G1/G2/G3)
- distance: INTEGER ⭐ Phase 3-2で取得中
- track_type: TEXT ⭐ Phase 3-2で取得中
- track_condition: TEXT ⭐ Phase 3-2で取得中
- horse_count: INTEGER ⭐ Phase 3-2で取得中
- is_grade_race: BOOLEAN
```

---

## 🔧 よく使うコマンド

### Phase 3-2（レース詳細取得）

#### 進捗確認
```bash
# 基本表示
python check_race_progress.py

# 詳細表示（グレード別・競馬場別）
python check_race_progress.py --verbose
```

#### バッチ処理実行
```bash
# 100件ずつ処理（推奨）
python batch_race_detail.py --limit 100

# 重賞のみ処理
python batch_race_detail.py --grade-only

# 待機時間を調整
python batch_race_detail.py --limit 100 --sleep 5
```

#### ログ確認
```bash
# 最新ログ
tail -100 logs/batch_race_detail_*.log

# エラー確認
grep "ERROR\|❌" logs/batch_race_detail_*.log

# 成功件数
grep "✅" logs/batch_race_detail_*.log | wc -l
```

---

## ⚠️ 注意事項

### アクセス制限
- 各レース処理後に**3秒待機**（デフォルト）
- **100件ずつ**分割実行を推奨
- 短時間の大量アクセスでIP制限の可能性

### データの注意点
- 有効な予想: 9,262件（temp形式67件を除く）
- 重賞予想: 1,619件（分析に十分）
- **未来のレース**は詳細情報が未公開のため「不明」になる（正常）
- 2025年8月以降のレースは未開催の可能性

### 実行環境
- 必ず仮想環境を有効化: `source venv/Scripts/activate`
- Python 3.12以上
- ChromeDriverがインストール済み
- loguruパッケージが必要: `pip install loguru`

---

## 🐛 トラブルシューティング

### ChromeDriverエラー
```bash
# Chromeプロセス強制終了
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T
```

### 途中で停止した場合
```bash
# 進捗確認
python check_race_progress.py

# 続きから実行（自動的に未取得分から再開）
python batch_race_detail.py --limit 100
```

### ログ確認
```bash
# 最新のログファイルを確認
ls -lt logs/

# ログ内容を確認
tail -100 logs/batch_race_detail_*.log
```

---

## 📚 ドキュメント

- [CURRENT_STATUS.md](CURRENT_STATUS.md) - 現在の詳細状況
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - プロジェクトサマリー
- [新しいチャットでの再開ガイド.md](新しいチャットでの再開ガイド.md) - 新チャット再開手順
- [SETUP.md](SETUP.md) - 初期セットアップガイド

---

## 🔗 リンク

- **GitHubリポジトリ**: https://github.com/obnvpn2-cpu/yosouka-ai
- **データソース**: https://netkeiba.com

---

## 📄 ライセンス

個人利用のみ

---

## 🙏 利用規約遵守

- netkeiba.comの利用規約を遵守
- 適切な間隔でリクエストを実行
- 個人利用の範囲内での使用に限定
- データの商用利用は禁止

---

## 🎯 次のステップ

### 1. Phase 3-2を完了（残り957件）
```bash
# 100件ずつ実行（推奨）
python batch_race_detail.py --limit 100
python check_race_progress.py

# 繰り返し...
```

### 2. データ品質検証（全データ取得後）
```bash
python << 'EOF'
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

# 芝/ダートの分布
cursor.execute("SELECT track_type, COUNT(*) FROM races WHERE track_type != '不明' GROUP BY track_type")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}件")

conn.close()
EOF
```

### 3. Phase 4へ移行（Phase 3-2完了後）
- 的中率・回収率の計算
- 重賞に強い予想家の特定
- ランキング生成

---

## 🎉 マイルストーン

- [x] **予想家データ取得**: 187人完了（100%）
- [x] **race_id更新**: 997件完了（99.3%）
- [ ] **レース詳細取得**: 40/997件（4%）← **現在のマイルストーン**
- [ ] **データ分析開始**: Phase 4
- [ ] **予想家ランキング**: TOP20リスト生成
- [ ] **Web UI**: データ可視化

---

**最終更新**: 2025/11/30 22:00  
**プロジェクト進捗**: Phase 3-2（レース詳細取得）実行中 - 4%完了

🎯 **現在の達成率: 約65%**
