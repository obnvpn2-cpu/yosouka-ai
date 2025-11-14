# 競馬予想家分析AI

netkeiba掲載の予想家の過去成績を分析し、重賞レースにおける的中率・回収率が高い予想家を推薦するシステム

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
│   ├── analyzer/        # 分析ロジック
│   ├── api/             # FastAPI エンドポイント
│   ├── models/          # データベースモデル
│   └── utils/           # ユーティリティ
├── frontend/            # フロントエンドUI
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── public/
├── data/                # データ保存
├── tests/               # テストコード
└── docs/                # ドキュメント
```

## セットアップ

### 1. 環境構築

```bash
# プロジェクトのクローン
cd keiba-yosoka-ai

# Python仮想環境の作成
python -m venv venv

# 仮想環境の有効化 (Windows)
venv\Scripts\activate

# 必要なパッケージのインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env` ファイルを作成:

```
DATABASE_URL=sqlite:///./data/keiba.db
NETKEIBA_USERNAME=your_username
NETKEIBA_PASSWORD=your_password
```

### 3. データベースの初期化

```bash
python backend/init_db.py
```

### 4. スクレイピング実行

```bash
python backend/scraper/main.py
```

### 5. APIサーバーの起動

```bash
uvicorn backend.api.main:app --reload
```

### 6. フロントエンドの起動

```bash
cd frontend
npm install
npm start
```

## 開発フェーズ

- [x] Phase 1: プロジェクトセットアップ
- [ ] Phase 2: スクレイピング実装
- [ ] Phase 3: データベース設計
- [ ] Phase 4: 分析機能実装
- [ ] Phase 5: API実装
- [ ] Phase 6: フロントエンド実装
- [ ] Phase 7: デプロイ

## ライセンス

個人利用のみ

## 注意事項

- netkeiba.comの利用規約を遵守すること
- 過度なアクセスを避け、適切な間隔でリクエストすること
- 個人利用の範囲内での使用に限定
