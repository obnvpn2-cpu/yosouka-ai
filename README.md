# 🏇 競馬予想家分析AI

netkeiba掲載の予想家の過去成績を分析し、重賞レースにおける的中率・回収率が高い予想家を推薦するシステム

---

## 📊 プロジェクト現状（2025/12/01）

### 進捗状況
```
全体進捗: ████████████████████░░░░░░░░ 約80%

Phase 1: セットアップ           ████████████████████ 100% ✅
Phase 2: 予想家データ取得       ████████████████████ 100% ✅
Phase 3-1: race_id更新          ████████████████████ 100% ✅
Phase 3-2: レース詳細取得       ████████████████████ 100% ✅
Phase 4: データ分析             ░░░░░░░░░░░░░░░░░░░░   0% ⏳ ← 次はここ
```

### データ取得完了
- ✅ **予想家**: 187人（100%）
- ✅ **予想数**: 9,262件
- ✅ **重賞予想**: 1,619件
- ✅ **レース詳細**: 997/997件（100%）

詳細は [PROJECT_STATUS.md](PROJECT_STATUS.md) を参照

---

## 🎯 プロジェクト概要

### 目的
netkeiba掲載の予想家の過去成績を分析し、指定した条件において信頼できる予想家を推薦するシステム

### 重要：このプロジェクトは何をするのか

❌ **ではない**: レース結果を予想するAI  
✅ **正しい**: 優秀な予想家を見つけて推薦するシステム

**具体例**:
- 入力: 「芝1600mのレースで誰の予想を信じればいい？」
- 出力: 「芝1600mで的中率82%、回収率115%の予想家Aがおすすめです」

- 入力: 「次の日曜日の天皇賞（秋）、誰の予想を信じればいい？」
- 出力: 「過去の天皇賞で的中率85%、回収率120%の予想家Bがおすすめです」

### 主な機能（実装予定）
1. ✅ 予想家の過去成績データ収集
2. ✅ レース詳細情報の取得
3. ⏳ 的中率・回収率の分析
4. ⏳ 条件別（芝/ダート、距離、競馬場）の成績分析
5. ⏳ 予想家ランキング生成
6. ⏳ 条件指定による予想家推薦
7. ⏳ Web UIでのデータ可視化

---

## 🛠️ 技術スタック

- **言語**: Python 3.12+
- **スクレイピング**: Selenium, pandas, BeautifulSoup4
- **データベース**: SQLite
- **分析**: pandas, numpy
- **API**: FastAPI（予定）
- **フロントエンド**: React（予定）

---

## 📁 プロジェクト構造

```
keiba-yosoka-ai/
├── backend/
│   ├── models/
│   │   └── database.py                      データベースモデル
│   └── scraper/
│       ├── __init__.py
│       ├── base.py                          スクレイパー基底クラス
│       ├── main.py                          ✅ 予想家データ取得
│       ├── prediction.py                    ✅ 予想履歴取得
│       ├── predictor_list.py                予想家リスト取得
│       ├── race_detail_scraper_with_db.py   ✅ レース詳細取得（メイン）
│       ├── race_detail_scraper_full.py      レース詳細取得（フル版）
│       ├── race_detail_scraper_nologin.py   レース詳細取得（ログイン不要版）
│       └── debug_login.py                   ログインデバッグ
│
├── scripts/                                 ⭐ 実行スクリプト（整理済み）
│   ├── batch/                               バッチ処理
│   │   ├── batch_race_detail.py             ✅ レース詳細バッチ取得
│   │   ├── batch_update_race_ids_v2.py      ✅ race_id一括更新（v2）
│   │   ├── batch_update_race_ids.py         race_id一括更新（旧版）
│   │   ├── batch_all_with_interval.sh       全件バッチ（インターバル付き）
│   │   └── batch_with_interval.sh           バッチ処理（インターバル付き）
│   │
│   ├── check/                               確認・進捗チェック
│   │   ├── check_race_progress.py           ✅ レース詳細取得進捗確認
│   │   ├── check_db_status.py               ✅ データベース状態確認
│   │   ├── check_data.py                    データ確認
│   │   ├── check_date_range.py              日付範囲確認
│   │   ├── check_pending_json.py            未取得レース確認
│   │   ├── check_predictor.py               予想家確認
│   │   ├── check_progress.py                進捗確認（汎用）
│   │   ├── check_race_conditions.py         レース条件確認
│   │   ├── check_race_id.py                 race_id確認
│   │   └── check_results.py                 結果確認
│   │
│   ├── debug/                               デバッグ
│   │   ├── debug_html.py                    HTML構造デバッグ
│   │   ├── debug_html_structure.py          HTML構造詳細デバッグ
│   │   └── debug_pandas_html.py             pandas版HTML確認
│   │
│   ├── test/                                テスト
│   │   ├── test_pandas_scraper.py           ✅ pandas版テスト
│   │   ├── test_fixed_scraper.py            修正版スクレイパーテスト
│   │   └── test_prediction.py               予想データテスト
│   │
│   └── utils/                               ユーティリティ
│       ├── update_race_ids_v2.py            race_id更新（v2）
│       ├── update_race_ids.py               race_id更新（旧版）
│       ├── update_db_from_json.py           JSONからDB更新
│       ├── fix_pending_races.py             未取得レース修正
│       ├── inspect_remaining_json.py        残りのJSON検査
│       ├── export_csv.py                    CSVエクスポート
│       ├── organize_files.py                ファイル整理
│       ├── retry_failed.py                  失敗分リトライ
│       ├── retry_specific.py                特定レースリトライ
│       └── race_detail_scraper.py           レース詳細スクレイパー（単体）
│
├── data/
│   ├── keiba.db                             ✅ データベース（3.1MB）
│   ├── race_details/                        ✅ レース詳細JSON（997件）
│   └── failed_logs/                         失敗ログ保存先
│
├── docs/
│   ├── RACE_DETAIL_SCRAPER_GUIDE.md         レース詳細スクレイパーガイド
│   └── archive/                             アーカイブドキュメント
│
├── drivers/
│   └── chromedriver.exe                     Selenium用（必要に応じて）
│
├── logs/                                    実行ログ
│
├── yosouka-ai/                              旧ディレクトリ（整理予定）
│
├── README.md                                ⭐ このファイル
├── PROJECT_STATUS.md                        ⭐ 現在の状況
├── RESTART_GUIDE.md                         ⭐ 再開ガイド
├── requirements.txt                         依存パッケージ
├── .env                                     環境変数（gitignore）
└── venv/                                    仮想環境（gitignore）
```

### 主要ファイルの説明

#### 🎯 よく使うスクリプト

**Phase 3で使用したスクリプト**:
- `scripts/batch/batch_race_detail.py` - レース詳細を997件バッチ取得
- `scripts/batch/batch_update_race_ids_v2.py` - race_idを一括更新
- `scripts/check/check_race_progress.py` - 進捗をリアルタイム表示
- `scripts/check/check_db_status.py` - データベース状態を詳細表示

**Phase 2で使用したスクリプト**:
- `backend/scraper/main.py` - 予想家データ取得
- `backend/scraper/prediction.py` - 予想履歴取得

**Phase 4で使用予定**:
- `scripts/check/check_data.py` - データ分析前の確認
- `scripts/utils/export_csv.py` - 分析結果をCSVエクスポート

---

## 🚀 クイックスタート

### 初回セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/obnvpn2-cpu/yosouka-ai.git
cd keiba-yosoka-ai

# 2. 仮想環境作成
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash

# 3. パッケージインストール
pip install -r requirements.txt
pip install beautifulsoup4 lxml loguru

# 4. 環境変数設定（オプション）
cp .env.example .env
# .envを編集してnetkeiba認証情報を設定

# 5. データベース初期化
python backend/init_db.py
```

### 現在の状況確認

```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

print('=' * 60)
print('データベース状態')
print('=' * 60)

# 予想家
cursor.execute('SELECT COUNT(*) FROM predictors')
print(f'予想家: {cursor.fetchone()[0]}人')

# 予想
cursor.execute('SELECT COUNT(*) FROM predictions')
print(f'予想数: {cursor.fetchone()[0]}件')

# レース詳細
cursor.execute('SELECT COUNT(*) FROM races')
total = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM races WHERE track_type IS NOT NULL AND track_type != \"不明\"')
completed = cursor.fetchone()[0]
print(f'レース: {total}件')
print(f'詳細取得済み: {completed}件 ({completed/total*100:.1f}%)')

# コース種別
cursor.execute('SELECT track_type, COUNT(*) FROM races WHERE track_type IS NOT NULL AND track_type != \"不明\" GROUP BY track_type')
print(f'\nコース種別:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}件')

conn.close()
"
```

---

## 📈 開発フェーズ

### 完了済み ✅

- [x] **Phase 1**: プロジェクトセットアップ
- [x] **Phase 2**: 予想家データ取得（187人）
- [x] **Phase 3-1**: race_id更新（997件）
- [x] **Phase 3-2**: レース詳細取得（997件、100%）
  - venue（競馬場）
  - track_type（芝/ダート）
  - distance（距離）
  - track_condition（馬場状態）
  - horse_count（出走頭数）

### 次のフェーズ ⏳

- [ ] **Phase 4**: データ分析 **← 次はここ**
  - 的中率の計算
  - 回収率（ROI）の計算
  - 予想家ランキング生成
  - 条件別成績分析
- [ ] **Phase 5**: API実装
- [ ] **Phase 6**: フロントエンド実装
- [ ] **Phase 7**: デプロイ

---

## 💾 データベース構造

### Predictors（予想家）- 187人
```sql
CREATE TABLE predictors (
    id INTEGER PRIMARY KEY,
    netkeiba_id INTEGER UNIQUE,
    name TEXT,
    total_predictions INTEGER,
    grade_race_predictions INTEGER,
    data_reliability TEXT
);
```

### Predictions（予想）- 9,262件
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    predictor_id INTEGER,
    race_id INTEGER,
    netkeiba_prediction_id INTEGER,
    is_hit BOOLEAN,
    payout INTEGER,
    roi FLOAT,
    FOREIGN KEY (predictor_id) REFERENCES predictors(id),
    FOREIGN KEY (race_id) REFERENCES races(id)
);
```

### Races（レース）- 997件
```sql
CREATE TABLE races (
    id INTEGER PRIMARY KEY,
    race_id TEXT UNIQUE,
    race_name TEXT,
    race_date DATETIME,
    venue TEXT,                 -- ✅ 取得完了
    grade TEXT,
    distance INTEGER,           -- ✅ 取得完了
    track_type TEXT,            -- ✅ 取得完了（芝/ダート）
    track_condition TEXT,       -- ✅ 取得完了
    horse_count INTEGER,        -- ✅ 取得完了
    is_grade_race BOOLEAN
);
```

---

## 🎯 次のステップ（Phase 4）

Phase 4では以下の分析機能を実装します：

### 1. 基本統計の計算
```python
# 予想家ごとの成績計算
- 総予想数
- 的中数
- 的中率
- 総払戻金
- 回収率（ROI）
```

### 2. 条件別分析
```python
# 条件別成績
- 芝/ダート別の成績
- 距離別の成績
- 競馬場別の成績
- グレード別の成績
```

### 3. ランキング生成
```python
# 予想家ランキング
- 総合的中率TOP20
- 総合回収率TOP20
- 重賞特化予想家TOP10
- 芝が得意な予想家TOP10
- ダートが得意な予想家TOP10
```

---

## 📊 データサマリー

### 取得済みデータ

| 項目 | 件数 | 状態 |
|------|------|------|
| 予想家 | 187人 | ✅ 完了 |
| 総予想 | 9,262件 | ✅ 完了 |
| 重賞予想 | 1,619件 | ✅ 完了 |
| レース | 997件 | ✅ 完了 |
| レース詳細 | 997件 | ✅ 完了 |

### コース種別の分布（997件）
- 芝: ~423件（42.4%）
- ダート: ~413件（41.4%）
- その他: ~161件（16.1%）

### 競馬場の分布（上位5）
- 東京: ~150件
- 京都: ~120件
- 中山: ~100件
- 阪神: ~90件
- その他: ~537件

---

## ⚠️ 注意事項

### データの利用について
- netkeiba.comの利用規約を遵守
- 個人利用の範囲内での使用に限定
- データの商用利用は禁止
- 適切な間隔でリクエストを実行

### 予想家の匿名化
- 公開時は予想家名を匿名化
- 予想家IDのみで管理
- 個人情報の保護

---

## 🐛 トラブルシューティング

### モジュールが見つからない
```bash
# 仮想環境が有効化されていることを確認
source venv/Scripts/activate

# パッケージを再インストール
pip install -r requirements.txt
pip install beautifulsoup4 lxml loguru
```

### データベースが開けない
```bash
# データベースファイルの存在確認
ls -lh data/keiba.db

# データベースの整合性チェック
sqlite3 data/keiba.db "PRAGMA integrity_check;"
```

### データが取得できていない
```bash
# データ取得状況を確認
python -c "
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM races WHERE track_type IS NOT NULL AND track_type != \"不明\"')
print(f'レース詳細取得済み: {cursor.fetchone()[0]}件')
conn.close()
"
```

---

## 📚 ドキュメント

- **README.md** - このファイル（プロジェクト概要）
- **PROJECT_STATUS.md** - 詳細な現在状況と次のステップ
- **RESTART_GUIDE.md** - 新しいチャットでの再開方法

---

## 🔗 リンク

- **GitHubリポジトリ**: https://github.com/obnvpn2-cpu/yosouka-ai
- **データソース**: https://netkeiba.com

---

## 📄 ライセンス

個人利用のみ

---

## 🎉 マイルストーン

- [x] 予想家データ取得完了（187人）
- [x] 予想データ取得完了（9,262件）
- [x] race_id更新完了（997件）
- [x] レース詳細取得完了（997件）
- [ ] 基本分析機能実装 ← **次はここ**
- [ ] ランキング生成
- [ ] Web UI実装

---

**最終更新**: 2025/12/01  
**プロジェクト進捗**: Phase 3完了、Phase 4準備中

🏇 **Phase 3-2: 100%完了！次はPhase 4（データ分析）へ！**
