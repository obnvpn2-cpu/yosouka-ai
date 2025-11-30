# 🏇 競馬予想家分析AI

netkeiba掲載の予想家の過去成績を分析し、重賞レースにおける的中率・回収率が高い予想家を推薦するシステム

---

## 📊 プロジェクト現状（2025/11/30）

- **進捗**: Phase 3-1完了 → Phase 3-2準備完了
- **予想家データ**: 187/186人完了（100%）✅
- **有効予想数**: 9,262件 ✅
- **重賞予想数**: 1,619件 ✅
- **race_id更新**: 完了（99.3%）✅
- **レース詳細情報**: 0/997件 ⏳

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
- **スクレイピング**: Selenium, BeautifulSoup4
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
│   │   ├── main.py                    ✅ 予想家データ取得
│   │   ├── prediction.py              ✅ 予想履歴取得
│   │   ├── update_race_ids_v2.py      ✅ race_id更新
│   │   ├── batch_update_race_ids_v2.py ✅ 一括更新
│   │   └── race_detail_scraper.py     ⏳ レース詳細取得
│   ├── models/
│   │   └── database.py                # データベースモデル
│   └── database.py                    # DB接続
├── data/
│   └── keiba.db                       # SQLiteデータベース
├── logs/                              # 実行ログ
├── docs/                              # ドキュメント
├── drivers/
│   └── chromedriver.exe               # Selenium用
├── venv/                              # Python仮想環境
├── .env                               # 環境変数（認証情報）
├── check_db_status.py                 # 進捗確認スクリプト
├── README.md                          # このファイル
├── CURRENT_STATUS.md                  # 現在の詳細状況
└── PROJECT_SUMMARY.md                 # プロジェクトサマリー
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
venv\Scripts\activate  # Windows

# 3. パッケージインストール
pip install -r requirements.txt

# 4. 環境変数設定
copy .env.example .env
# .envを編集してnetkeiba認証情報を設定

# 5. データベース初期化
python backend/init_db.py
```

### 現在の進捗確認

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai
python check_db_status.py
```

**出力例**:
```
処理済み予想家: 187/186人 (100.5%)
有効な予想数: 9,262件
重賞予想数: 1,619件
temp形式のrace_id: 67件
正しいrace_id: 997件
レース詳細: 0/997件（次のタスク）
```

---

## 📈 開発フェーズ

- [x] **Phase 1**: プロジェクトセットアップ ✅
- [x] **Phase 2**: 予想家データ取得（187人完了）✅
- [x] **Phase 3-1**: race_id更新（99.3%完了）✅
- [ ] **Phase 3-2**: レース詳細情報取得 ⏳
- [ ] **Phase 4**: 分析機能実装
- [ ] **Phase 5**: API実装
- [ ] **Phase 6**: フロントエンド実装
- [ ] **Phase 7**: デプロイ

### 現在のフェーズ詳細（Phase 3-2）

**目的**: 997件のレースについて詳細情報を取得

**取得する情報**:
- レース基本情報（距離、トラック、天候、馬場状態）
- レース結果（着順、タイム、オッズ）
- 払い戻し情報
- ラップタイム

**使用スクリプト**:
- `race_detail_scraper.py` - レース詳細取得
- `batch_update_race_details.py` - 一括更新（作成予定）

**推定所要時間**: 3-4時間

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
- venue: TEXT
- grade: TEXT (G1/G2/G3)
- distance: INTEGER（未取得）
- track_type: TEXT（未取得）
- is_grade_race: BOOLEAN
```

---

## 🔧 よく使うコマンド

### 進捗確認
```bash
python check_db_status.py
```

### レース詳細取得（テスト）
```bash
python race_detail_scraper.py
```

### レース詳細一括取得（次のタスク）
```bash
python batch_update_race_details.py --batch-size 100
```

### ログ確認
```bash
# 最新ログ
tail -100 logs/*.log

# エラー確認
grep "ERROR" logs/*.log
```

---

## ⚠️ 注意事項

### アクセス制限
- netkeiba.comへのアクセスは適切な間隔で実行
- 各リクエスト後に2秒待機
- バッチ処理は100件ごとに30秒休憩

### データの正確性
- 有効な予想: 9,262件（temp形式67件を除く）
- 重賞予想: 1,619件（分析に十分）
- 未来のレース予想には的中情報なし

### 環境
- Python 3.12以上推奨
- ChromeDriver必須
- Windows環境で動作確認済み

---

## 🐛 トラブルシューティング

### ChromeDriverエラー
```bash
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T
```

### データベースロック
```bash
# バックアップから復元
cp data/keiba.db.backup data/keiba.db
```

### ログ確認
```bash
ls -lt logs/  # 最新のログファイルを確認
```

---

## 📚 ドキュメント

- [CURRENT_STATUS.md](CURRENT_STATUS.md) - 現在の詳細状況
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - プロジェクトサマリー
- [RACE_DETAIL_SCRAPER_GUIDE.md](RACE_DETAIL_SCRAPER_GUIDE.md) - レース詳細スクレイパーガイド
- [NEW_CHAT_START_GUIDE.md](NEW_CHAT_START_GUIDE.md) - 新しいチャット開始ガイド

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

1. **レース詳細取得**（Phase 3-2）
   - `batch_update_race_details.py` 作成
   - 997件のレース詳細を自動取得

2. **データ分析**（Phase 4）
   - 的中率・回収率の計算
   - 重賞に強い予想家の特定
   - ランキング生成

3. **API実装**（Phase 5）
   - FastAPIエンドポイント作成
   - 予想家検索API
   - ランキングAPI

---

**最終更新**: 2025/11/30  
**プロジェクト進捗**: Phase 3-1完了 → Phase 3-2準備完了

🎉 **現在の達成率: 約60%**
