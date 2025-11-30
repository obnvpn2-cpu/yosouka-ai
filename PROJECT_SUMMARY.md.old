# 🏇 競馬予想家分析AI - プロジェクトサマリー

**作成日**: 2025/11/23  
**プロジェクト進捗**: Phase 3-1 - race_id更新中

---

## 📌 このファイルの使い方

**新しいチャットを開始する際に:**
1. このファイル（PROJECT_SUMMARY.md）を最初にアップロード
2. CURRENT_STATUS.md をアップロード
3. 「続きからやりたい」と伝える

これだけでClaudeが状況を把握して作業を継続できます。

---

## 🎯 プロジェクトの目的

netkeiba掲載の予想家の過去成績を分析し、**重賞レースにおける的中率・回収率が高い予想家を推薦**するシステム

---

## 📊 現在の状況（一目でわかる）

```
Phase 2完了: ████████████████████████████████ 100%
Phase 3-1:   ████████░░░░░░░░░░░░░░░░░░░░░░ 約2%

予想家データ: 187/186人 (100%)
総予想数: 9,329件
race_id更新: 進行中（temp形式 約8,900件 → 正しいID 約200件）
レース詳細: 未取得
```

**現在の作業**:
```bash
# バッチ処理実行中
python batch_update_race_ids_v2.py --batch-size 100
```

**次にやること**（race_id更新完了後）:
```bash
# レース詳細情報の取得
python race_detail_scraper.py
```

---

## 🔧 技術スタック

- **バックエンド**: Python 3.12, SQLite, Selenium
- **スクレイピング**: BeautifulSoup4, Selenium WebDriver
- **データベース**: SQLite (data/keiba.db)
- **データソース**: netkeiba.com
- **環境**: Windows MINGW64, venv

---

## 📁 プロジェクト構造

```
keiba-yosoka-ai/
├── backend/scraper/
│   ├── main.py                        ✅ 予想家データ取得（完了）
│   ├── prediction.py                  ✅ 予想履歴取得（完了）
│   ├── update_race_ids_v2.py          🔄 race_id更新
│   ├── batch_update_race_ids_v2.py    🔄 一括更新（実行中）
│   └── race_detail_scraper.py         ⏳ レース詳細取得（次フェーズ）
├── data/keiba.db                      📊 データベース
├── logs/                              📝 実行ログ
├── check_db_status.py                 🔍 進捗確認スクリプト
├── CURRENT_STATUS.md                  📋 現在の詳細状況
└── README.md                          📖 プロジェクト概要
```

---

## 🚀 開発フェーズ

- [x] Phase 1: プロジェクトセットアップ ✅
- [x] Phase 2: 予想家データ取得（187人）✅
- [x] Phase 3-1: race_id更新（進行中）🔄
- [ ] Phase 3-2: レース詳細情報取得
- [ ] Phase 4: 分析機能実装
- [ ] Phase 5: API実装
- [ ] Phase 6: フロントエンド実装
- [ ] Phase 7: デプロイ

---

## 💡 重要なコマンド

### 進捗確認
```bash
python check_db_status.py
```

出力例：
```
処理済み予想家: 187/186人 (100.5%)
総予想数: 9,329件
temp形式のrace_id: 8,995件
正しいrace_id: 167件
```

### race_id更新（個別）
```bash
python update_race_ids_v2.py --limit 10 --offset 0
```

### race_id更新（バッチ一括）
```bash
python batch_update_race_ids_v2.py --batch-size 100
```

### ログ確認
```bash
# 最新ログ
tail -100 logs/batch_update_race_ids_*.log

# エラーのみ
grep "ERROR" logs/*.log
```

### トラブルシューティング
```bash
# Chromeプロセス強制終了
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T
```

---

## ⚠️ 注意事項

### アクセス制限
- 各race_id取得後に2秒待機
- 100件ごとに30秒休憩
- 短時間の大量アクセスでIP制限（24時間）の可能性

### データの特徴
- temp形式のrace_id: `temp_542_5548369`
- 正しいrace_id: `202508040411`（12桁）
- 複数の予想が同じレースを参照している場合あり

### 実行環境
- 仮想環境を有効化: `source venv/Scripts/activate`
- Python 3.12以上
- ChromeDriverがインストール済み

---

## 📊 データベース構造

### Predictors（予想家）- 187人
- `id`, `netkeiba_id`, `name`
- `total_predictions` - 総予想数
- `grade_race_predictions` - 重賞予想数

### Predictions（予想）- 9,329件
- `id`, `predictor_id`, `race_id`
- `netkeiba_prediction_id` - race_id取得に使用
- `is_hit` - 的中フラグ
- `payout` - 払戻金

### Races（レース）- 9,162件
- `id`, `race_id` - ⚠️ 現在temp形式が多数
- `race_name`, `race_date`
- `grade` - G1/G2/G3（詳細情報未取得）
- `distance`, `track_type` - （詳細情報未取得）

---

## 🔗 参考リンク

- **GitHubリポジトリ**: https://github.com/obnvpn2-cpu/yosouka-ai
- **データソース**: https://netkeiba.com

---

## 📝 次のステップ（簡易版）

1. **race_id更新の完了を待つ**（現在進行中）
   - バッチ処理が自動実行中
   - 推定完了時間: 12-15時間

2. **更新完了の確認**
   ```bash
   python check_db_status.py
   ```

3. **レース詳細情報取得へ移行**（Phase 3-2）
   ```bash
   python race_detail_scraper.py
   ```

4. **データ分析開始**（Phase 4）
   - 的中率・回収率の計算
   - 重賞に強い予想家の特定

---

## 🆘 トラブル時の対処

### Q: バッチ処理が止まった
A: ログを確認
```bash
tail -100 logs/batch_update_race_ids_*.log
```

### Q: UNIQUE制約エラー
A: 修正版（v2）を使用
```bash
python batch_update_race_ids_v2.py
```

### Q: ChromeDriverエラー
A: プロセスを強制終了
```bash
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T
```

---

## 🎯 最終目標

- **データ取得**: 187人全員（9,329件の予想）✅
- **race_id更新**: 9,162件全て正しいIDに更新（進行中）
- **レース詳細**: 距離・トラック・天候などの情報を全レースで取得
- **分析**: 的中率・回収率の計算
- **推薦**: 重賞に強い予想家TOP20のランキング

---

**現在のマイルストーン**: race_id更新中（約2%完了）  
**次のマイルストーン**: race_id更新完了 → レース詳細取得開始

詳細は `CURRENT_STATUS.md` を参照してください。
