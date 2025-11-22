# 🏇 レース詳細スクレイパー使い方ガイド

**作成日**: 2025/11/19  
**ファイル**: `race_detail_scraper.py`

---

## 📌 概要

`race_detail_scraper.py`は、netkeiba.comのレース結果詳細ページから**すべての情報**を取得するスクレイパーです。

### 取得できる情報

#### 1️⃣ レース基本情報
- レース名
- グレード（G1/G2/G3）
- 開催日、発走時刻
- 競馬場名、レースナンバー
- 距離、トラック（芝/ダート）
- 天候、馬場状態
- 条件（牝馬限定/牡馬混合など）
- 負担重量（ハンデ/定量/別定）
- 頭数
- 賞金

#### 2️⃣ レース結果（各馬）
- 着順
- 枠番、馬番
- 馬名
- 性齢
- 斤量
- 騎手名
- タイム
- 着差
- 人気
- 単勝オッズ
- 後3F
- コーナー通過順
- 厩舎（所属と調教師名）
- 馬体重（増減も）

#### 3️⃣ 払い戻し情報
- 単勝、複勝
- 枠連、馬連、ワイド
- 馬単
- 3連複、3連単
- 各券種の結果、払戻金、人気

#### 4️⃣ コーナー通過順
- 各コーナーの通過順位

#### 5️⃣ ラップタイム
- 累積タイム（通過秒数）
- 区間タイム（ハロンごと）
- ペース（S/M/Hなど）

---

## 🚀 使い方

### 基本的な使い方

```python
from race_detail_scraper import RaceDetailScraper

# スクレイパーを初期化
scraper = RaceDetailScraper()

try:
    # レースIDを指定して取得
    race_id = "202505050211"  # 12桁のrace_id
    result = scraper.get_race_details(race_id)
    
    if result:
        print(f"レース名: {result['race_info']['race_name']}")
        print(f"グレード: {result['race_info']['grade']}")
        print(f"距離: {result['race_info']['distance']}m")
        print(f"出走頭数: {len(result['race_results'])}頭")
        
finally:
    # 必ず閉じる
    scraper.close_driver()
```

### テスト実行

```bash
# スクリプトを直接実行
python race_detail_scraper.py
```

実行すると：
- サンプルレース（202505050211）の情報を取得
- `race_202505050211_details.json` にJSON形式で保存
- 標準出力に主要な情報を表示

---

## 📊 出力データ構造

```json
{
  "race_id": "202505050211",
  "race_info": {
    "race_name": "アルゼンチン共和国杯",
    "grade": "G2",
    "post_time": "15:30",
    "track_type": "芝",
    "distance": 2500,
    "weather": "曇",
    "track_condition": "良",
    "venue": "東京",
    "kaisai_count": 5,
    "day": 2,
    "race_condition": "サラ系３歳以上",
    "race_class": "オープン",
    "weight_type": "ハンデ",
    "horse_count": 18,
    "prize_money": 5700
  },
  "race_results": [
    {
      "rank": 1,
      "bracket": 7,
      "horse_number": 13,
      "horse_name": "ミステリーウェイ",
      "sex_age": "セ7",
      "jockey_weight": 56.0,
      "jockey": "松本",
      "time": "2:30.2",
      "margin": "",
      "popularity": 9,
      "odds": 27.7,
      "last_3f": "34.6",
      "corner_pass": "1-1-1-1",
      "trainer_location": "栗東",
      "trainer_name": "小林",
      "horse_weight": 500,
      "weight_change": -2
    }
    // ... 他の馬
  ],
  "payback": {
    "単勝": {
      "result": "13",
      "payout": "2,770円",
      "popularity": "9人気"
    },
    "複勝": {
      "result": "13\n18\n6",
      "payout": "550円\n180円\n200円",
      "popularity": "10人気2人気3人気"
    }
    // ... 他の券種
  },
  "corner_pass": {
    "1コーナー": "13-10,11(2,14)3(5,9)...",
    "2コーナー": "13=10,11(2,3,14)...",
    "3コーナー": "13-10,11,14(2,3,9)...",
    "4コーナー": "13(10,11,14)9(2,3)..."
  },
  "lap_times": {
    "cumulative": ["7.7", "19.0", "30.6", ...],
    "intervals": ["7.7", "11.3", "11.6", ...],
    "pace": "S"
  },
  "scraped_at": "2025-11-19T10:30:45.123456"
}
```

---

## 🔧 主なクラスとメソッド

### RaceDetailScraper クラス

#### メソッド

##### `setup_driver()`
Seleniumドライバーをセットアップ（ヘッドレスモード）

##### `close_driver()`
ドライバーを閉じる（必ず呼び出す）

##### `get_race_details(race_id: str) -> Optional[Dict]`
レース詳細情報を取得

**引数**:
- `race_id` (str): 12桁のレースID（例: "202505050211"）

**戻り値**:
- 成功時: レース情報の辞書
- 失敗時: None

##### `_extract_race_info() -> Dict`
レース基本情報を抽出（内部メソッド）

##### `_extract_race_results() -> List[Dict]`
レース結果（各馬）を抽出（内部メソッド）

##### `_extract_payback_info() -> Dict`
払い戻し情報を抽出（内部メソッド）

##### `_extract_corner_pass() -> Dict`
コーナー通過順を抽出（内部メソッド）

##### `_extract_lap_times() -> Dict`
ラップタイムを抽出（内部メソッド）

---

## ⚠️ 注意事項

### アクセス制限
- 各リクエスト後に2秒待機
- 連続実行時は適切な間隔を空ける
- 短時間の大量アクセスでIP制限の可能性

### エラーハンドリング
- ページが存在しない場合は`None`を返す
- 要素が見つからない場合は空文字列や0を設定
- ログに詳細なエラー情報を出力

### 必須要件
- Chrome/ChromeDriverがインストール済み
- Python 3.8以上
- 必要なパッケージ：
  ```
  selenium
  loguru
  ```

---

## 📝 実装のポイント

### HTMLの構造に基づく実装

#### レース名
```python
race_name_elem = driver.find_element(By.CLASS_NAME, "RaceName")
race_name = race_name_elem.text.strip().split('\n')[0]
```

#### グレード判定
```python
if 'Icon_GradeType1' in grade_class:
    grade = 'G1'
elif 'Icon_GradeType2' in grade_class:
    grade = 'G2'
elif 'Icon_GradeType3' in grade_class:
    grade = 'G3'
```

#### 距離・トラック
```python
distance_match = re.search(r'(芝|ダート)(\d+)m', race_data01)
track_type = distance_match.group(1)  # 芝 or ダート
distance = int(distance_match.group(2))  # 2500
```

#### 払い戻し情報
```python
payback_wrapper = driver.find_element(By.CLASS_NAME, "ResultPaybackLeftWrap")
tables = payback_wrapper.find_elements(By.CLASS_NAME, "Payout_Detail_Table")
```

#### コーナー通過順
```python
corner_table = driver.find_element(By.CSS_SELECTOR, "table.Corner_Num")
```

#### ラップタイム
```python
lap_table = driver.find_element(By.CLASS_NAME, "Race_HaronTime")
rows = lap_table.find_elements(By.CSS_SELECTOR, "tbody tr.HaronTime")
# rows[0]: 累積タイム
# rows[1]: 区間タイム
```

---

## 🎯 次のステップ

### 1. データベース更新スクリプトの作成
`race_detail_scraper.py`で取得したデータをDBに保存

### 2. バッチ処理の実装
複数のレースを一括取得

### 3. エラーリトライの強化
失敗したレースを再試行

---

## 📚 関連ファイル

- `race_detail_scraper.py` - スクレイパー本体
- `RACE_DETAIL_SCRAPER_GUIDE.md` - このファイル
- `race_*.json` - テスト実行時の出力

---

## 🐛 トラブルシューティング

### Q: ChromeDriverが見つからない
A: ChromeDriverをインストール
```bash
# Windowsの場合
# 手動でダウンロードしてPATHに追加

# Linuxの場合
sudo apt-get install chromium-chromedriver
```

### Q: 要素が見つからないエラー
A: ページの構造が変更された可能性。ログを確認して該当箇所を調整

### Q: タイムアウトエラー
A: ネットワーク環境を確認。待機時間を延長
```python
self.driver.implicitly_wait(20)  # 10→20秒に延長
```

---

**作成完了！次回はこのスクレイパーをDB更新に統合します。**
