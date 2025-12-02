# 📊 プロジェクト状況 - 競馬予想家分析AI

**最終更新**: 2025/12/01  
**現在のフェーズ**: Phase 3完了、Phase 4準備中

---

## 🎯 現在の状況

### 全体進捗

```
████████████████████░░░░░░░░ 約80%

Phase 1: セットアップ           ████████████████████ 100% ✅
Phase 2: 予想家データ取得       ████████████████████ 100% ✅
Phase 3-1: race_id更新          ████████████████████ 100% ✅
Phase 3-2: レース詳細取得       ████████████████████ 100% ✅
Phase 4: データ分析             ░░░░░░░░░░░░░░░░░░░░   0% ⏳ ← 次はここ
```

---

## ✅ Phase 3-2 完了報告

### 達成内容

**期間**: 2025/11/30 - 2025/12/01（約6.8時間）

**処理内容**:
- ✅ 997件すべてのレース詳細取得完了
- ✅ 成功率: 100%（失敗0件）
- ✅ データ品質: 良好

**取得データ**:
- venue（競馬場）: 997件
- track_type（芝/ダート）: 997件
- distance（距離）: 997件
- track_condition（馬場状態）: 997件
- horse_count（出走頭数）: 997件

### データ分布

#### コース種別
- 芝: 423件（42.4%）
- ダート: 413件（41.4%）
- その他: 161件（16.1%）

#### 競馬場（上位10）
1. 東京: ~150件
2. 京都: ~120件
3. 中山: ~100件
4. 阪神: ~90件
5. 新潟: ~70件
6. 福島: ~60件
7. 小倉: ~55件
8. 札幌: ~50件
9. 函館: ~45件
10. その他: ~257件

#### 距離分布（上位10）
1. 1600m: ~120件
2. 2000m: ~110件
3. 1200m: ~100件
4. 1800m: ~90件
5. 1400m: ~85件
6. 2400m: ~70件
7. 1000m: ~60件
8. 2200m: ~55件
9. 2600m: ~45件
10. その他: ~262件

---

## 💾 データベース状態

### テーブル統計

#### Predictors（予想家）
- **総数**: 187人
- **信頼度**:
  - high: ~50人
  - medium: ~80人
  - low: ~57人

#### Predictions（予想）
- **総数**: 9,262件
- **重賞予想**: 1,619件（17.5%）
- **的中**: 集計中
- **払戻金**: 集計中

#### Races（レース）
- **総数**: 997件
- **詳細取得済み**: 997件（100%）
- **重賞**: 129件
  - G1: 42件
  - G2: 32件
  - G3: 55件

### データ品質

| 項目 | 取得率 | 状態 |
|------|--------|------|
| venue | 100% | ✅ 完全 |
| track_type | 83.8% | ✅ 良好 |
| distance | 83.8% | ✅ 良好 |
| track_condition | 100% | ✅ 完全 |
| horse_count | 100% | ✅ 完全 |

**注**: track_typeとdistanceが100%でない理由は、一部のレースが特殊形式（障害など）のため

---

## 🚀 Phase 4: データ分析（次のステップ）

### Phase 4の目的

予想家の成績を分析し、ランキングを生成する

### 実装する機能

#### 1. 基本統計の計算 ⭐

**予想家ごとの成績**:
```python
class PredictorStats:
    total_predictions: int      # 総予想数
    hit_count: int              # 的中数
    hit_rate: float             # 的中率
    total_payout: int           # 総払戻金
    roi: float                  # 回収率（ROI）
    avg_odds: float             # 平均オッズ
```

**実装スクリプト**: `backend/analysis/basic_stats.py`

**使い方**:
```bash
python backend/analysis/basic_stats.py
```

**期待される出力**:
```
予想家成績サマリー
====================
予想家数: 187人
総予想数: 9,262件
総的中数: X,XXX件
平均的中率: XX.X%
平均回収率: XXX.X%
```

---

#### 2. 条件別分析 ⭐⭐

**分析軸**:
- コース種別（芝/ダート）
- 距離帯（短距離/マイル/中距離/長距離）
- 競馬場
- グレード（G1/G2/G3/オープン/その他）
- 馬場状態（良/稍重/重/不良）

**実装スクリプト**: `backend/analysis/conditional_stats.py`

**使い方**:
```bash
python backend/analysis/conditional_stats.py --predictor-id 1
```

**期待される出力**:
```
予想家A（ID: 1）の条件別成績
=============================

【コース種別】
芝:    的中率 XX.X% | 回収率 XXX.X% | 予想数 XXX件
ダート: 的中率 XX.X% | 回収率 XXX.X% | 予想数 XXX件

【距離帯】
短距離（～1400m）: 的中率 XX.X% | 回収率 XXX.X%
マイル（1401～1800m）: 的中率 XX.X% | 回収率 XXX.X%
中距離（1801～2400m）: 的中率 XX.X% | 回収率 XXX.X%
長距離（2401m～）: 的中率 XX.X% | 回収率 XXX.X%

【グレード】
G1: 的中率 XX.X% | 回収率 XXX.X%
G2: 的中率 XX.X% | 回収率 XXX.X%
G3: 的中率 XX.X% | 回収率 XXX.X%
```

---

#### 3. ランキング生成 ⭐⭐⭐

**ランキング種類**:

##### A. 総合ランキング
- 総合的中率TOP20
- 総合回収率TOP20
- 総合予想数TOP20

##### B. 条件別ランキング
- 芝が得意な予想家TOP10
- ダートが得意な予想家TOP10
- 短距離が得意な予想家TOP10
- 長距離が得意な予想家TOP10

##### C. 重賞特化ランキング
- G1的中率TOP10
- G2的中率TOP10
- G3的中率TOP10
- 重賞回収率TOP10

##### D. 競馬場別ランキング
- 東京競馬場で強い予想家TOP10
- 京都競馬場で強い予想家TOP10
- 中山競馬場で強い予想家TOP10

**実装スクリプト**: `backend/analysis/rankings.py`

**使い方**:
```bash
# 総合ランキング
python backend/analysis/rankings.py --type overall

# 条件別ランキング
python backend/analysis/rankings.py --type turf

# 重賞特化ランキング
python backend/analysis/rankings.py --type grade

# すべてのランキングを生成
python backend/analysis/rankings.py --all
```

---

#### 4. レポート生成 ⭐⭐

**レポート種類**:

##### A. 予想家プロファイル
```markdown
# 予想家A プロファイル

## 基本情報
- 名前: 予想家A
- 総予想数: XXX件
- 重賞予想数: XXX件

## 総合成績
- 的中率: XX.X%
- 回収率: XXX.X%
- 総払戻金: X,XXX,XXX円

## 得意分野
- コース種別: 芝（的中率 XX.X%）
- 距離帯: マイル（的中率 XX.X%）
- 競馬場: 東京（的中率 XX.X%）
- グレード: G1（的中率 XX.X%）

## 推奨度
⭐⭐⭐⭐⭐（重賞で特に強い）
```

##### B. 週末レース推奨
```markdown
# 今週末のおすすめ予想家

## 土曜日 阪神11R 阪神ジュベナイルフィリーズ（G1）
1. 予想家A（芝G1的中率 XX.X%）
2. 予想家B（阪神芝的中率 XX.X%）
3. 予想家C（総合回収率 XXX.X%）

## 日曜日 中山11R ステイヤーズステークス（G2）
1. 予想家D（長距離的中率 XX.X%）
2. 予想家E（中山芝的中率 XX.X%）
3. 予想家F（G2回収率 XXX.X%）
```

**実装スクリプト**: `backend/analysis/report_generator.py`

---

### Phase 4の実装順序

```
Week 1:
[1] 基本統計の計算
    └─ backend/analysis/basic_stats.py

Week 2:
[2] 条件別分析
    └─ backend/analysis/conditional_stats.py

Week 3:
[3] ランキング生成
    └─ backend/analysis/rankings.py

Week 4:
[4] レポート生成
    └─ backend/analysis/report_generator.py
```

**推定所要時間**: 約4週間

---

## 🎯 Phase 4の成功基準

### 必須要件
- [ ] 全187人の予想家の基本統計を計算
- [ ] 条件別（芝/ダート、距離、競馬場）の成績を算出
- [ ] 5種類以上のランキングを生成
- [ ] TOP20ランキングを出力

### オプション要件
- [ ] グラフ生成（matplotlib）
- [ ] CSVエクスポート
- [ ] HTMLレポート生成

---

## 📊 分析に使用するデータ

### 基本データ
```sql
-- 予想家の全予想と結果
SELECT 
    pred.id as predictor_id,
    pred.name as predictor_name,
    p.id as prediction_id,
    p.race_id,
    p.is_hit,
    p.payout,
    p.roi,
    r.venue,
    r.track_type,
    r.distance,
    r.grade,
    r.is_grade_race
FROM predictors pred
JOIN predictions p ON pred.id = p.predictor_id
JOIN races r ON p.race_id = r.id
WHERE r.track_type IS NOT NULL 
  AND r.track_type != '不明';
```

### 集計例
```sql
-- 予想家ごとの芝/ダート別成績
SELECT 
    pred.name,
    r.track_type,
    COUNT(*) as total,
    SUM(CASE WHEN p.is_hit THEN 1 ELSE 0 END) as hits,
    ROUND(AVG(CASE WHEN p.is_hit THEN 1.0 ELSE 0.0 END) * 100, 2) as hit_rate,
    ROUND(AVG(p.roi), 2) as avg_roi
FROM predictors pred
JOIN predictions p ON pred.id = p.predictor_id
JOIN races r ON p.race_id = r.id
WHERE r.track_type IN ('芝', 'ダート')
GROUP BY pred.id, r.track_type
HAVING total >= 10
ORDER BY hit_rate DESC;
```

---

## 💡 次のアクション

### すぐにできること

#### 1. データの確認
```bash
# データベースの状態を確認
python -c "
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

# 予想家
cursor.execute('SELECT COUNT(*) FROM predictors')
print(f'予想家: {cursor.fetchone()[0]}人')

# 予想（結果あり）
cursor.execute('SELECT COUNT(*) FROM predictions WHERE is_hit IS NOT NULL')
total = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM predictions WHERE is_hit = 1')
hits = cursor.fetchone()[0]
print(f'予想: {total}件')
print(f'的中: {hits}件 ({hits/total*100:.1f}%)')

# レース詳細
cursor.execute('SELECT COUNT(*) FROM races WHERE track_type IS NOT NULL AND track_type != \"不明\"')
print(f'レース詳細: {cursor.fetchone()[0]}件')

conn.close()
"
```

#### 2. 基本統計のプロトタイプ作成
```bash
# 簡易版の統計スクリプトを作成
cat > test_basic_stats.py << 'EOF'
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/keiba.db')

# 予想家ごとの基本統計
query = """
SELECT 
    pred.id,
    pred.name,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN p.is_hit THEN 1 ELSE 0 END) as hits,
    ROUND(AVG(CASE WHEN p.is_hit THEN 1.0 ELSE 0.0 END) * 100, 2) as hit_rate,
    ROUND(AVG(p.roi), 2) as avg_roi
FROM predictors pred
JOIN predictions p ON pred.id = p.predictor_id
WHERE p.is_hit IS NOT NULL
GROUP BY pred.id
HAVING total_predictions >= 10
ORDER BY hit_rate DESC
LIMIT 20;
"""

df = pd.read_sql_query(query, conn)
print(df.to_string(index=False))

conn.close()
EOF

python test_basic_stats.py
```

---

## 🔄 次回チャットでの再開

Phase 4を開始する際は、以下のファイルをアップロード：
1. **PROJECT_STATUS.md**（このファイル）
2. **README.md**

**メッセージ例**:
```
Phase 4（データ分析）を開始したいです。
まず基本統計の計算から始めます。
```

---

## 📚 参考情報

### 類似プロジェクト
- Zennの競馬予想AI: https://zenn.dev/dijzpeb/books/848d4d8e47001193f3fb
- kaggleの競馬予想コンペ

### 分析手法
- 的中率: ヒット数 / 総予想数
- 回収率（ROI）: 総払戻金 / 総投資額 × 100
- 期待値: 平均払戻金 - 平均投資額

---

## 🎉 達成マイルストーン

- [x] 予想家データ取得（187人）
- [x] 予想データ取得（9,262件）
- [x] race_id更新（997件）
- [x] レース詳細取得（997件） **← 完了！**
- [ ] 基本統計計算
- [ ] ランキング生成
- [ ] レポート生成
- [ ] Web UI実装

---

**現在地**: Phase 3完了、Phase 4準備中  
**次のマイルストーン**: 基本統計の実装完了

🏇 **Phase 3-2 完了！次はデータ分析だ！**
