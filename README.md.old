# 競馬予想家分析AI

netkeiba掲載の予想家の過去成績を分析し、重賞レースにおける的中率・回収率が高い予想家を推薦するシステム

## 📊 プロジェクト現状（2025/11/15）

- **進捗**: Phase 2実装中（スクレイピング安定化）
- **データ取得**: 18/186人完了（9.7%）
- **総予想数**: 732件
- **重賞予想数**: 158件

詳細は [CURRENT_STATUS.md](CURRENT_STATUS.md) を参照

---

## プロジェクト概要

- **目的**: 重賞レースで信頼できる予想家を推薦
- **データソース**: netkeiba.com
- **データ量**: 予想家1人あたり過去50件

## 技術スタック

### バックエンド
- Python 3.12+
- FastAPI
- SQLAlchemy
- BeautifulSoup4 / Selenium
- pandas, numpy

### フロントエンド
- React + TypeScript
- Material-UI
- Recharts

### データベース
- SQLite (開発)
- PostgreSQL (本番)

## ディレクトリ構造

```
keiba-yosoka-ai/
├── backend/              # バックエンドAPI
│   ├── scraper/         # スクレイピング機能
│   │   ├── main.py      # メインスクリプト
│   │   ├── prediction.py # 予想履歴取得（要最新版適用）
│   │   └── base.py      # 基底クラス
│   ├── analyzer/        # 分析ロジック（Phase 4）
│   ├── api/             # FastAPI エンドポイント（Phase 5）
│   ├── models/          # データベースモデル
│   │   └── database.py
│   └── utils/           # ユーティリティ
├── frontend/            # フロントエンドUI（Phase 6）
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── public/
├── data/                # データ保存
│   └── keiba.db        # SQLiteデータベース
├── logs/                # スクレイピングログ
├── tests/               # テストコード
├── docs/                # ドキュメント
├── README.md           # このファイル
├── SETUP.md            # セットアップガイド
└── CURRENT_STATUS.md   # 現在の詳細状況
```

## クイックスタート

### 初回セットアップ

詳細は [SETUP.md](SETUP.md) を参照

```bash
# 1. 仮想環境作成
python -m venv venv
venv\Scripts\activate

# 2. パッケージインストール
pip install -r requirements.txt

# 3. 環境変数設定
copy .env.example .env
# .envを編集してnetkeiba認証情報を設定

# 4. データベース初期化
python backend/init_db.py
```

### スクレイピング実行

⚠️ **重要**: 最新版の`prediction.py`を適用してから実行してください

```bash
# Pythonパス設定
export PYTHONPATH=$(pwd)

# テスト実行（1人）
python backend/scraper/main.py --limit 1 --offset 0

# 本実行（10人ずつ推奨）
python backend/scraper/main.py --limit 10 --offset 0
```

### 進捗確認

```bash
python << 'EOF'
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
print(f"処理済み: {cursor.fetchone()[0]}/186人")
conn.close()
EOF
```

---

## 開発フェーズ

- [x] Phase 1: プロジェクトセットアップ
- [x] Phase 2: スクレイピング実装（安定化作業中 🔄）
- [x] Phase 3: データベース設計
- [ ] Phase 4: 分析機能実装
- [ ] Phase 5: API実装
- [ ] Phase 6: フロントエンド実装
- [ ] Phase 7: デプロイ

### Phase 2の詳細状況

**実装済み**:
- ✅ 予想家リスト取得
- ✅ 予想履歴取得（過去50件）
- ✅ 的中情報・払戻金取得
- ✅ データベース保存
- ✅ リトライ機能
- ✅ エラーハンドリング

**改善中**:
- 🔄 Seleniumの安定化（成功率50% → 95%目標）
- 🔄 プロセス管理の改善
- 🔄 待機時間の最適化

---

## 🚨 重要な注意事項

### 最新版prediction.pyの適用が必須

現在のバージョンでは成功率が約50%です。最新版（`prediction_final.py`）を適用してください：

```bash
# ダウンロードした最新版を配置
cp ~/Downloads/prediction_final.py backend/scraper/prediction.py
```

詳細は [CURRENT_STATUS.md](CURRENT_STATUS.md) の「最優先事項」を参照

### アクセス制限について

- 各予想家の処理後に15秒待機
- 10人または5人ずつ分割実行を推奨
- 短時間の大量アクセスでIP制限（24時間）の可能性

### データについて

- 未来のレース予想には的中情報なし
- 分析時は `race_date < datetime.now()` でフィルタリング必要

---

## トラブルシューティング

### ChromeDriverエラー
```bash
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T
```

### ログ確認
```bash
tail -100 logs/scraper_*.log
```

### データベース確認
```bash
sqlite3 data/keiba.db
.tables
SELECT COUNT(*) FROM predictors;
.quit
```

詳細は [SETUP.md](SETUP.md) のトラブルシューティングセクションを参照

---

## 📚 ドキュメント

- [SETUP.md](SETUP.md) - 詳細なセットアップ手順
- [CURRENT_STATUS.md](CURRENT_STATUS.md) - 現在の状況と次のステップ

---

## データベース構造

### Predictors（予想家）
- `id`, `netkeiba_id`, `name`
- `total_predictions` - 総予想数
- `grade_race_predictions` - 重賞予想数
- `data_reliability` - 信頼度（low/medium/high）

### Predictions（予想）
- `id`, `predictor_id`, `race_id`
- `is_hit` - 的中フラグ
- `payout` - 払戻金
- `roi` - 回収率

### Races（レース）
- `id`, `race_id`, `race_name`
- `grade` - グレード（G1/G2/G3）
- `is_grade_race` - 重賞フラグ

---

## GitHubリポジトリ

https://github.com/obnvpn2-cpu/yosouka-ai

---

## ライセンス

個人利用のみ

## 利用規約遵守

- netkeiba.comの利用規約を遵守すること
- 適切な間隔でリクエストを行うこと（現在: 15秒間隔）
- 個人利用の範囲内での使用に限定
