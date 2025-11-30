# 🏇 競馬予想家分析AI - プロジェクトサマリー

**作成日**: 2025/11/16  
**最終更新**: 2025/11/30  
**プロジェクト進捗**: Phase 3-2（レース詳細取得）開始 - 4%完了

---

## 📌 このファイルの使い方

**新しいチャットを開始する際に:**
1. このファイル（PROJECT_SUMMARY.md）を最初にアップロード
2. CURRENT_STATUS.md をアップロード
3. 「Phase 3-2の続きをやりたい」と伝える

これだけでClaudeが状況を把握して作業を継続できます。

---

## 🎯 プロジェクトの目的

netkeiba掲載の予想家の過去成績を分析し、**重賞レースにおける的中率・回収率が高い予想家を推薦**するシステム

---

## 📊 現在の状況（一目でわかる）

```
全体進捗: ████████████████░░░░░░░░░░░░ 約65%

Phase 1: セットアップ           ████████████████████ 100% ✅
Phase 2: 予想家データ取得       ████████████████████ 100% ✅
Phase 3-1: race_id更新          ████████████████████ 100% ✅
Phase 3-2: レース詳細取得       █░░░░░░░░░░░░░░░░░░░   4% 🔄
Phase 4: データ分析             ░░░░░░░░░░░░░░░░░░░░   0% ⏳
```

**データ取得状況**:
- 予想家: 187/186人（100%）✅
- 予想数: 9,262件 ✅
- 重賞予想: 1,619件 ✅
- レース数: 997件
- レース詳細: 40/997件（4%）🔄

**次にやること**:
```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai
python batch_race_detail.py --limit 100
```

---

## 🔧 技術スタック

- **バックエンド**: Python 3.12, FastAPI, SQLAlchemy, Selenium
- **スクレイピング**: Selenium, loguru
- **データベース**: SQLite (data/keiba.db)
- **データソース**: netkeiba.com
- **環境**: Windows MINGW64, venv

---

## 📁 プロジェクト構造

```
keiba-yosoka-ai/
├── backend/
│   ├── scraper/
│   │   ├── main.py                        ✅ 予想家データ取得
│   │   ├── prediction.py                  ✅ 予想履歴取得
│   │   ├── update_race_ids_v2.py          ✅ race_id更新
│   │   └── race_detail_scraper_with_db.py ⭐ レース詳細取得（新）
│   ├── models/database.py
│   └── database.py
├── data/
│   ├── keiba.db                           ⭐ データベース
│   └── race_details/                      ⭐ レース詳細JSON
├── logs/                                  ⭐ 実行ログ
├── batch_race_detail.py                   ⭐ バッチ処理（新）
├── check_race_progress.py                 ⭐ 進捗確認（新）
├── venv/                                  仮想環境
├── .env                                   netkeiba認証情報
├── CURRENT_STATUS.md                      ⭐ 詳細な現在状況
├── PROJECT_SUMMARY.md                     ⭐ このファイル
└── README.md                              プロジェクト概要
```

---

## 🚀 開発フェーズ

- [x] **Phase 1**: プロジェクトセットアップ ✅
- [x] **Phase 2**: 予想家データ取得（187人完了）✅
- [x] **Phase 3-1**: race_id更新（99.3%完了）✅
- [ ] **Phase 3-2**: レース詳細取得（4%完了）🔄 **← 現在ここ**
- [ ] **Phase 4**: 分析機能実装 ⏳
- [ ] **Phase 5**: API実装 ⏳
- [ ] **Phase 6**: フロントエンド実装 ⏳
- [ ] **Phase 7**: デプロイ ⏳

---

## 📋 Phase 3-2の詳細（現在実行中）

### 目的
997件のレースについて詳細情報を取得し、データ分析の準備を完了する

### 取得する情報
- **venue**（競馬場）: 東京、京都、中山など
- **track_type**（コース種別）: 芝、ダート
- **distance**（距離）: 1200m、1600m、2000mなど
- **track_condition**（馬場状態）: 良、稍重、重、不良
- **horse_count**（出走頭数）

### 使用スクリプト
1. **race_detail_scraper_with_db.py** - スクレイパー本体
2. **batch_race_detail.py** - バッチ処理
3. **check_race_progress.py** - 進捗確認

### 実行方法
```bash
# 100件ずつ処理（推奨）
python batch_race_detail.py --limit 100

# 進捗確認
python check_race_progress.py

# 全件処理
python batch_race_detail.py
```

### 推定所要時間
- 100件: 約40分
- 全件（997件）: 約6-7時間

---

## 💡 重要なコマンド

### 進捗確認
```bash
# 基本表示
python check_race_progress.py

# 詳細表示（グレード別・競馬場別）
python check_race_progress.py --verbose
```

### バッチ処理実行
```bash
# 100件ずつ処理（推奨）
python batch_race_detail.py --limit 100

# 重賞のみ処理
python batch_race_detail.py --grade-only

# 待機時間を調整
python batch_race_detail.py --limit 100 --sleep 5
```

### ログ確認
```bash
# 最新ログ
tail -100 logs/batch_race_detail_*.log

# エラー確認
grep "ERROR\|❌" logs/batch_race_detail_*.log

# 成功件数
grep "✅" logs/batch_race_detail_*.log | wc -l
```

### トラブルシューティング
```bash
# Chromeプロセス強制終了
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T

# データベース確認
python << 'EOF'
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM races WHERE track_type != '不明'")
print(f"詳細取得済み: {cursor.fetchone()[0]}件")
conn.close()
EOF
```

---

## ⚠️ 注意事項

### アクセス制限
- 各レース処理後に**3秒待機**（デフォルト）
- **100件ずつ**分割実行を推奨
- 短時間の大量アクセスでIP制限の可能性

### データの注意点
- **未来のレース**は詳細情報が未公開のため「不明」になる（正常）
- 2025年8月以降のレースは未開催の可能性
- 分析時は過去のレースのみをフィルタリング

### 実行環境
- 必ず仮想環境を有効化: `source venv/Scripts/activate`
- Python 3.12以上
- ChromeDriverがインストール済み
- loguruパッケージが必要: `pip install loguru`

---

## 📊 データベース構造

### Predictors（予想家）- 187人
- `id`, `netkeiba_id`, `name`
- `total_predictions` - 総予想数
- `grade_race_predictions` - 重賞予想数
- `data_reliability` - 信頼度（low/medium/high）

### Predictions（予想）- 9,262件
- `id`, `predictor_id`, `race_id`
- `is_hit` - 的中フラグ
- `payout` - 払戻金
- `roi` - 回収率（計算済み）

### Races（レース）- 997件
- `id`, `race_id`, `race_name`
- `grade` - グレード（G1/G2/G3）
- `venue` - 競馬場 ⭐ Phase 3-2で取得中
- `track_type` - コース種別（芝/ダート）⭐ Phase 3-2で取得中
- `distance` - 距離 ⭐ Phase 3-2で取得中
- `track_condition` - 馬場状態 ⭐ Phase 3-2で取得中
- `is_grade_race` - 重賞フラグ

---

## 🔗 参考リンク

- **GitHubリポジトリ**: https://github.com/obnvpn2-cpu/yosouka-ai
- **データソース**: https://netkeiba.com

---

## 📝 次のステップ（簡易版）

### 1. Phase 3-2を完了（残り957件）
```bash
# 100件ずつ実行
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
- 的中率の計算
- 回収率（ROI）の計算
- 予想家ランキング生成
- 重賞特化予想家の特定

---

## 🆘 トラブル時の対処

### Q: ChromeDriverエラー
A: プロセスを強制終了
```bash
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T
```

### Q: 途中で停止した
A: 進捗を確認して続きから実行
```bash
python check_race_progress.py
# 出力を確認して続きから実行
python batch_race_detail.py --limit 100
```

### Q: エラー率が高い（10%以上）
A: 待機時間を増やす
```bash
python batch_race_detail.py --limit 50 --sleep 5
```

---

## 🎯 マイルストーン

- [x] **予想家データ取得**: 187人完了（100%）
- [x] **race_id更新**: 997件完了（99.3%）
- [ ] **レース詳細取得**: 40/997件（4%）← **現在のマイルストーン**
- [ ] **データ分析開始**: Phase 4
- [ ] **予想家ランキング**: TOP20リスト生成
- [ ] **Web UI**: データ可視化

---

## 🔄 新しいチャットでの再開

1. **ファイルをアップロード**:
   - PROJECT_SUMMARY.md（このファイル）
   - CURRENT_STATUS.md

2. **メッセージ**:
   ```
   Phase 3-2の続きをやりたいです。
   レース詳細取得を継続します。
   ```

3. **Claudeが提案**:
   - 進捗確認コマンド
   - 次の実行コマンド
   - トラブルシューティング（必要時）

---

## 💡 成功のポイント

### データ取得
- ✅ 100件ずつ分割実行
- ✅ 定期的な進捗確認
- ✅ ログのモニタリング

### 品質管理
- ✅ エラー率を5%以下に維持
- ✅ 定期的なバックアップ
- ✅ データの整合性チェック

### 効率化
- ✅ 夜間や空き時間に長時間実行
- ✅ 並行作業（スクレイピング中に別作業）
- ✅ 自動化スクリプトの活用

---

**現在のマイルストーン**: レース詳細取得 40/997件（4%）  
**次のマイルストーン**: レース詳細取得 500/997件（50%）  
**最終目標**: Phase 4（データ分析）開始

詳細は `CURRENT_STATUS.md` を参照してください。 🏇
