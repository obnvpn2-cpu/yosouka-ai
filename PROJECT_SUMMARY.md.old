# 🏇 競馬予想家分析AI - プロジェクトサマリー

**作成日**: 2025/11/16  
**プロジェクト進捗**: Phase 2（データ取得）実行中 - 26.9%完了

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
進捗: ████████░░░░░░░░░░░░░░░░░░░░ 26.9%

処理済み予想家: 50/186人
総予想数: 約2,400件
重賞予想数: 約380件
残り実行回数: 約14回（10人ずつ）
```

**次にやること**:
```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai
python backend/scraper/main.py --limit 10 --offset 50
```

---

## 🔧 技術スタック

- **バックエンド**: Python 3.12, FastAPI, SQLAlchemy, Selenium
- **データベース**: SQLite (data/keiba.db)
- **データソース**: netkeiba.com
- **環境**: Windows MINGW64, venv

---

## 📁 プロジェクト構造

```
keiba-yosoka-ai/
├── backend/
│   ├── scraper/
│   │   ├── main.py          ★ メインスクリプト（2025/11/16修正版）
│   │   ├── prediction.py    ★ 予想取得（安定版）
│   │   └── predictor_list.py
│   ├── models/database.py
│   └── database.py
├── data/
│   └── keiba.db            ★ データベース（50/186人分）
├── logs/                   ★ 実行ログ
├── venv/                   仮想環境
├── .env                    netkeiba認証情報
├── CURRENT_STATUS.md       ★ 詳細な現在状況
└── README.md               プロジェクト概要
```

---

## 🐛 最近修正したバグ

### main.pyの`--offset`バグ（2025/11/16修正）

**症状**: 
- `--offset 49`を指定しても無視されて最初（offset 0）から処理
- 既存データは重複チェックでスキップ
- 新しいデータが追加されない → 進捗が止まる

**原因**: 
- argparseが実装されていなかった

**修正**: 
- argparseで`--limit`と`--offset`を正しく処理
- 処理範囲のログ出力を追加

**結果**: 
- offset 49→50に正常に進行 ✅

---

## 🚀 開発フェーズ

- [x] Phase 1: プロジェクトセットアップ
- [x] Phase 2: スクレイピング実装（**実行中 26.9%** 🔄）
- [x] Phase 3: データベース設計
- [ ] Phase 4: 分析機能実装（データ取得完了後）
- [ ] Phase 5: API実装
- [ ] Phase 6: フロントエンド実装
- [ ] Phase 7: デプロイ

---

## 💡 重要なコマンド

### 進捗確認
```bash
python << 'EOF'
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
processed = cursor.fetchone()[0]
print(f"処理済み: {processed}/186人 ({processed/186*100:.1f}%)")
print(f"次: python backend/scraper/main.py --limit 10 --offset {processed}")
conn.close()
EOF
```

### スクレイピング実行
```bash
# 10人ずつ処理（推奨）
python backend/scraper/main.py --limit 10 --offset 50

# 1人だけテスト
python backend/scraper/main.py --limit 1 --offset 50

# テストモード（最初の5人）
python backend/scraper/main.py --test
```

### ログ確認
```bash
# 最新ログ
tail -100 logs/scraper_*.log

# 処理範囲の確認
grep "Processing predictors" logs/scraper_*.log

# エラー確認
grep "ERROR" logs/scraper_*.log
```

### トラブルシューティング
```bash
# Chromeプロセス強制終了
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T

# データベース確認
sqlite3 data/keiba.db
.tables
SELECT COUNT(*) FROM predictors;
.quit
```

---

## ⚠️ 注意事項

### アクセス制限
- 各予想家の処理後に**15秒待機**
- **10人ずつ**分割実行を推奨
- 短時間の大量アクセスでIP制限（24時間）の可能性

### 実行環境
- 必ず仮想環境を有効化: `source venv/Scripts/activate`
- Python 3.12以上
- ChromeDriverがインストール済み

### データの注意点
- 未来のレース予想には的中情報なし（is_hit=0, payout=0）
- 分析時は `race_date < datetime.now()` でフィルタリング必須

---

## 📊 データベース構造

### Predictors（予想家）
- `id`, `netkeiba_id`, `name`
- `total_predictions` - 総予想数
- `grade_race_predictions` - 重賞予想数
- `data_reliability` - 信頼度（low/medium/high）

### Predictions（予想）
- `id`, `predictor_id`, `race_id`
- `is_hit` - 的中フラグ
- `payout` - 払戻金
- `roi` - 回収率（計算済み）

### Races（レース）
- `id`, `race_id`, `race_name`
- `grade` - グレード（G1/G2/G3）
- `is_grade_race` - 重賞フラグ

---

## 🔗 参考リンク

- **GitHubリポジトリ**: https://github.com/obnvpn2-cpu/yosouka-ai
- **データソース**: https://netkeiba.com

---

## 📝 次のステップ（簡易版）

1. **データ取得を継続**（残り136人）
   ```bash
   python backend/scraper/main.py --limit 10 --offset 50
   ```

2. **データ品質検証**（全データ取得後）
   ```bash
   # 的中+配当データの確認
   python << 'EOF'
   import sqlite3
   conn = sqlite3.connect('data/keiba.db')
   cursor = conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM predictions WHERE is_hit = 1 AND payout > 0")
   print(f"的中+配当データ: {cursor.fetchone()[0]}件")
   conn.close()
   EOF
   ```

3. **Phase 4へ移行**（186人完了後）
   - 的中率・回収率の計算
   - 重賞に強い予想家の特定
   - ランキング生成

---

## 🆘 トラブル時の対処

### Q: offsetが進まない
A: main.pyが最新版（2025/11/16修正版）か確認
```bash
grep "argparse" backend/scraper/main.py
# 出力があればOK
```

### Q: ChromeDriverエラー
A: プロセスを強制終了
```bash
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T
```

### Q: データベースエラー
A: バックアップから復元
```bash
cp data/keiba.db.backup data/keiba.db
```

---

## 🎯 最終目標

- **データ取得**: 186人全員（約9,300件の予想）
- **分析**: 的中率・回収率の計算
- **推薦**: 重賞に強い予想家TOP20のランキング
- **可視化**: Web UIでデータ表示

---

**現在のマイルストーン**: データ取得 50/186人（26.9%）  
**次のマイルストーン**: データ取得 100/186人（53.8%）

詳細は `CURRENT_STATUS.md` を参照してください。
