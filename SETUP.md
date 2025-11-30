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
# Git Bashの場合
source venv/Scripts/activate

# PowerShellの場合（実行ポリシーエラーが出たら下記を実行）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## ステップ2: 依存パッケージのインストール

```bash
pip install -r requirements.txt

# 追加で必要なパッケージ
pip install loguru
```

## ステップ3: 環境設定

1. `.env.example`を`.env`にコピー
```bash
cp .env.example .env
```

2. `.env`ファイルを編集してnetkeiba認証情報を設定（オプション）
```
NETKEIBA_USERNAME=あなたのユーザー名
NETKEIBA_PASSWORD=あなたのパスワード
```

**注意**: Phase 3-2（レース詳細取得）ではログイン不要です。

## ステップ4: データベースの初期化

```bash
python backend/init_db.py
```

## ステップ5: Phase 3-2の実行

現在は Phase 3-2（レース詳細取得）を実行中です：

### 進捗確認
```bash
python check_race_progress.py
```

### レース詳細取得
```bash
# 100件ずつ処理（推奨）
python batch_race_detail.py --limit 100

# 進捗確認
python check_race_progress.py

# 繰り返し...
```

## トラブルシューティング

### エラー: ModuleNotFoundError

仮想環境が有効化されていることを確認してください。
```bash
source venv/Scripts/activate
```

### エラー: loguru not found

loguruをインストール:
```bash
pip install loguru
```

### ChromeDriverエラー

プロセスを強制終了:
```bash
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T
```

### 途中で停止した

進捗を確認して続きから実行:
```bash
# 進捗確認
python check_race_progress.py

# 続きから実行
python batch_race_detail.py --limit 100
```

## ログの確認

ログは`logs/`ディレクトリに保存されます：
```bash
# 最新のログを確認
tail -f logs/batch_race_detail_*.log

# エラーのみ確認
grep "ERROR\|❌" logs/batch_race_detail_*.log
```

## 次のステップ

Phase 3-2が完了したら、Phase 4（データ分析）に進みます。

詳細は [CURRENT_STATUS.md](CURRENT_STATUS.md) を参照してください。
