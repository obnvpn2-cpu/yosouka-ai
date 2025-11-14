# Phase 1 完了 - 次のステップ

## 🎉 Phase 1: データ収集基盤構築が完了しました！

以下のファイルが作成されました：

### プロジェクト構造
```
keiba-yosoka-ai/
├── README.md              # プロジェクト概要
├── SETUP.md               # セットアップガイド
├── requirements.txt       # 必要なパッケージ
├── .env.example           # 環境変数テンプレート
├── .gitignore            # Git除外ファイル
└── backend/
    ├── config.py         # アプリケーション設定
    ├── database.py       # データベース接続
    ├── init_db.py        # DB初期化スクリプト
    ├── models/
    │   └── database.py   # データベースモデル
    └── scraper/
        ├── base.py           # スクレイパーベースクラス
        ├── predictor_list.py # 予想家一覧取得
        ├── prediction.py     # 予想履歴取得
        └── main.py          # メインスクリプト
```

## ⚠️ 重要な注意事項

### 1. HTML構造の調整が必要

提供いただいたURLのページ構造を実際に確認して、スクレイパーのセレクタを調整する必要があります。

**確認すべきファイル:**
- `backend/scraper/predictor_list.py` （91行目〜）
- `backend/scraper/prediction.py` （52行目〜、145行目〜）

**調整方法:**
1. 実際のnetkeibaのページをブラウザで開く
2. 開発者ツール（F12）でHTML構造を確認
3. 適切なCSSセレクタやクラス名に修正

### 2. ログイン機能

有料会員の場合、ログインが必要なページがあるかもしれません。
`backend/scraper/base.py`の`login()`メソッドは基本的な実装ですが、
実際のログインフローに合わせて調整が必要な場合があります。

### 3. エンコーディング

netkeibaはEUC-JPを使用しています。文字化けが発生する場合は、
`base.py`の`get_page()`メソッドのencodingパラメータを調整してください。

## 📋 実行手順

### 1. セットアップ

```bash
# プロジェクトフォルダに移動
cd keiba-yosoka-ai

# 仮想環境作成
python -m venv venv

# 仮想環境有効化（Windows）
venv\Scripts\activate

# パッケージインストール
pip install -r requirements.txt

# 環境設定
copy .env.example .env
# .envファイルを編集してnetkeiba認証情報を設定

# データベース初期化
python backend/init_db.py
```

### 2. テスト実行

```bash
# 最初の5人の予想家のみ取得（テストモード）
python -m backend.scraper.main --test
```

### 3. 実行結果の確認

- `data/keiba.db` にSQLiteデータベースが作成されます
- `logs/` フォルダにログファイルが保存されます

データベースの内容を確認：
```bash
# SQLiteをインストール済みの場合
sqlite3 data/keiba.db "SELECT * FROM predictors LIMIT 10;"
```

または、DB Browser for SQLite等のGUIツールを使用

## 🔧 デバッグのヒント

### HTML構造の確認

実際に取得したHTMLを確認するには、`base.py`に以下を追加：

```python
# get_page() メソッド内
soup = BeautifulSoup(response.text, 'lxml')
# デバッグ用
with open('debug.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())
```

### ログレベルの変更

`.env`ファイルで：
```
LOG_LEVEL=DEBUG
```

## 📊 次のPhase（Phase 2: 分析機能）

Phase 1が成功したら、次は分析機能の実装です：

1. **予想家パフォーマンス分析**
   - 的中率・回収率の計算
   - 重賞特化成績の抽出
   - 条件別成績の集計

2. **統計計算**
   - サンプル数の集計
   - 信頼度の判定
   - 得意パターンの抽出

3. **ランキングロジック**
   - レース条件に基づく予想家推薦
   - 複数予想家の合議分析

## 🤔 質問があれば

Phase 1で問題が発生した場合、以下の情報を教えてください：

1. エラーメッセージの全文
2. ログファイルの内容
3. どのステップで問題が発生したか
4. 実際のnetkeibaのHTML構造（開発者ツールのスクリーンショット等）

それでは、まずはセットアップとテスト実行をお試しください！
