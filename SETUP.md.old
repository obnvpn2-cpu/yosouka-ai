# セットアップガイド

## 前提条件

- Windows
- Python 3.12.1
- VS Code

## ステップ1: プロジェクトの準備

1. プロジェクトフォルダに移動
```bash
cd keiba-yosoka-ai
```

2. Python仮想環境を作成
```bash
python -m venv venv
```

3. 仮想環境を有効化
```bash
# Windowsの場合
venv\Scripts\activate

# PowerShellの場合（実行ポリシーエラーが出たら下記を実行）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## ステップ2: 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## ステップ3: 環境設定

1. `.env.example`を`.env`にコピー
```bash
copy .env.example .env
```

2. `.env`ファイルを編集してnetkeiba認証情報を設定
```
NETKEIBA_USERNAME=あなたのユーザー名
NETKEIBA_PASSWORD=あなたのパスワード
```

## ステップ4: データベースの初期化

```bash
python backend/init_db.py
```

## ステップ5: テスト実行

最初は少数の予想家でテスト実行します：

```bash
python -m backend.scraper.main --test
```

これにより最初の5人の予想家のデータが取得されます。

## ステップ6: フル実行

テストが成功したら、全予想家のデータを取得：

```bash
python -m backend.scraper.main
```

⚠️ 注意: 全予想家の取得には時間がかかります（数時間〜）

## トラブルシューティング

### エラー: ModuleNotFoundError

仮想環境が有効化されていることを確認してください。
```bash
venv\Scripts\activate
```

### エラー: ログインに失敗

1. `.env`ファイルの認証情報が正しいか確認
2. netkeiba.comで実際にログインできるか確認
3. 有料会員でないとアクセスできないページもあります

### HTMLの構造が変わった場合

netkeibaのHTML構造が変更された場合、スクレイパーのコードを調整する必要があります。
実際のHTMLを確認して、`backend/scraper/`内のファイルを修正してください。

### リクエスト制限に引っかかった場合

`.env`ファイルの`SCRAPING_DELAY`を増やしてください（例: 5秒）

## ログの確認

ログは`logs/`ディレクトリに保存されます：
```bash
# 最新のログを確認
tail -f logs/scraper_*.log
```

## 次のステップ

Phase 1が完了したら、Phase 2（分析機能）に進みます。
