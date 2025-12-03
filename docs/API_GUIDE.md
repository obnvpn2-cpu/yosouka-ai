# Phase 4.3: API起動ガイド

## 📦 必要なパッケージのインストール

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai

# FastAPI関連パッケージをインストール
pip install fastapi uvicorn pydantic requests

# requirements.txtに追記
echo "fastapi" >> requirements.txt
echo "uvicorn[standard]" >> requirements.txt
echo "pydantic" >> requirements.txt
echo "requests" >> requirements.txt
```

---

## 🚀 API起動方法

### 方法1: Pythonで直接起動

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai

# APIサーバーを起動
python backend/api/api.py
```

**起動メッセージ**:
```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 方法2: Uvicornコマンドで起動

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai

# ホットリロード有効（開発用）
uvicorn backend.api.api:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔍 API動作確認

### ブラウザでアクセス

起動後、以下のURLにアクセス：

1. **ヘルスチェック**: http://localhost:8000/
2. **APIドキュメント（Swagger UI）**: http://localhost:8000/docs
3. **統計情報**: http://localhost:8000/api/stats
4. **検索条件の選択肢**: http://localhost:8000/api/options

### テストスクリプトで確認

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai

# 別のターミナルを開いて実行
python scripts/test/test_api.py
```

---

## 📡 エンドポイント一覧

### 1. ヘルスチェック
```
GET /
```

**レスポンス例**:
```json
{
  "status": "ok",
  "service": "競馬予想家分析API",
  "version": "1.0.0"
}
```

---

### 2. 統計情報取得
```
GET /api/stats
```

**レスポンス例**:
```json
{
  "total_predictors": 187,
  "total_predictions": 9262,
  "total_races": 997,
  "races_with_detail": 997,
  "min_predictions": 5
}
```

---

### 3. 検索条件の選択肢取得
```
GET /api/options
```

**レスポンス例**:
```json
{
  "venues": ["中京", "中山", "京都", "函館", ...],
  "track_types": ["ダート", "芝", "障害"],
  "distances": [1000, 1150, 1200, ...],
  "grades": ["G1", "G2", "G3", "オープン", "一般"],
  "min_predictions": 5
}
```

---

### 4. 予想家検索
```
POST /api/search
Content-Type: application/json
```

**リクエストボディ**:
```json
{
  "venue": "東京",              // 競馬場（オプション）
  "track_type": "芝",           // コース種別（オプション）
  "distances": [1600, 2000],    // 距離（オプション、複数選択可）
  "grade": "G1",                // グレード（オプション）
  "sort_by": "hit_rate",        // ソート基準（hit_rate or roi）
  "limit": 50                   // 取得件数
}
```

**レスポンス例**:
```json
{
  "total_count": 18,
  "avg_hit_rate": 16.35,
  "max_hit_rate": 40.0,
  "total_predictions": 98,
  "predictors": [
    {
      "predictor_id": 123,
      "predictor_name": "リアル両津",
      "netkeiba_id": 456789,
      "prediction_count": 5,
      "hit_count": 2,
      "hit_rate": 40.0,
      "total_payout": 1500,
      "avg_payout": 750.0,
      "roi_count": 0,
      "avg_roi": null
    },
    ...
  ]
}
```

---

## 🧪 curlでテスト

### 選択肢取得
```bash
curl http://localhost:8000/api/options
```

### 検索（東京競馬場の芝）
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "venue": "東京",
    "track_type": "芝",
    "sort_by": "hit_rate",
    "limit": 5
  }'
```

### 検索（芝1600m）
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "track_type": "芝",
    "distances": [1600],
    "sort_by": "hit_rate",
    "limit": 10
  }'
```

---

## 📝 開発Tips

### ホットリロード有効で起動
```bash
uvicorn backend.api.api:app --reload
```

コードを変更すると自動的にサーバーが再起動されます。

### ポート変更
```bash
uvicorn backend.api.api:app --port 8080
```

### ログレベル変更
```bash
uvicorn backend.api.api:app --log-level debug
```

---

## 🐛 トラブルシューティング

### ポート8000が使用中
```bash
# ポートを変更して起動
python backend/api/api.py  # api.pyを編集してポート変更

# または
uvicorn backend.api.api:app --port 8080
```

### データベースが見つからない
```bash
# プロジェクトルートから実行していることを確認
pwd
# 出力: ~/デスクトップ/repo/keiba-yosoka-ai

# data/keiba.dbが存在することを確認
ls -la data/keiba.db
```

### モジュールが見つからない
```bash
# 仮想環境が有効化されていることを確認
source venv/Scripts/activate

# パッケージを再インストール
pip install fastapi uvicorn pydantic
```

---

## 🎯 次のステップ

API起動が確認できたら、Phase 4.4（Webフロントエンド）に進みます。

Reactでフロントエンドを実装し、このAPIを呼び出します。
