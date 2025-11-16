# データ取得完了までのロードマップ

**作成日**: 2025/11/15
**戦略**: 選択肢A（Selenium改善）→ Playwright移行

---

## 📋 作成されたドキュメント

### 1. **OPTION_A_GUIDE.md** ⭐ 今すぐ読む
Seleniumでのデータ取得完了ガイド
- 改善版の適用手順
- 実行スケジュール
- トラブルシューティング

### 2. **FAILED_PREDICTORS.md**
失敗した予想家の記録（更新中）
- 各実行の成功/失敗記録
- リトライコマンド

### 3. **PLAYWRIGHT_MIGRATION.md**
Phase 4開始前のPlaywright移行ガイド
- 環境構築
- コード書き換え
- 性能比較

### 4. **prediction_final.py** ⭐ 今すぐ適用
Selenium最終改善版
- `--disable-blink-features=AutomationControlled`追加
- 自動化検知を無効化
- ウィンドウサイズ指定

---

## 🚀 今すぐやること（優先順位順）

### ステップ1: 最新版を適用（5分）

```bash
cd ~/デスクトップ/repo/keiba-yosoka-ai

# 最新版prediction.pyを適用
cp ~/Downloads/prediction_final.py backend/scraper/prediction.py

# main.pyの待機時間を延長（15秒 → 30秒）
# 手動で編集: backend/scraper/main.py
# time.sleep(15) → time.sleep(30)
```

### ステップ2: 進捗確認（2分）

```bash
export PYTHONPATH=$(pwd)

python << 'EOF'
import sqlite3
conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
processed = cursor.fetchone()[0]

print(f"処理済み: {processed}/186人")
print(f"残り: {186 - processed}人")
print(f"\n次の実行:")
print(f"python backend/scraper/main.py --limit 10 --offset {processed}")

conn.close()
EOF
```

### ステップ3: 次の10人を実行（約20分）

```bash
# プロセスクリーンアップ
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T

# 実行
export PYTHONPATH=$(pwd)
python backend/scraper/main.py --limit 10 --offset <前のステップで表示されたoffset>

# 失敗した予想家をメモ
```

### ステップ4: 失敗記録の更新（3分）

FAILED_PREDICTORS.mdに失敗した予想家を記録

### ステップ5: 休憩（30分〜1時間）

**重要**: 次の実行まで必ず休憩を取ってください

---

## 📊 現在の状況（2025/11/15時点）

| 項目 | 数値 |
|------|------|
| 処理済み予想家 | 30/186人（16.1%） |
| 成功予想家 | 20人 |
| 失敗予想家 | 10人 |
| 総予想数 | 1,182件 |
| 成功率 | 67% |

### 失敗した予想家リスト（リトライ必要）

**1回目**:
- めんふく (ID: 360)
- ぽた (ID: 495)
- こうせい (ID: 542)
- 妹尾和也 (ID: 539)
- オッズアナライザー (ID: 283)

**2回目**:
- 翔天 (ID: 670)
- メシ馬 (ID: 364)

**3回目**:
- Aiエスケープ (ID: 329)
- F4.Kazuma (ID: 531)
- 星野瑠利 (ID: 521)

**4回目**（現在）:
- アルゴスピーダー (ID: 110)
- 征木由基人 (ID: 261)
- 本島修司 (ID: 459)
- キノピー (ID: 282) ← 処理中に停止

---

## 📅 推定スケジュール

### 前提条件
- 1回の実行: 10人
- 1回の所要時間: 約20分（実行15分 + 記録5分）
- 休憩: 30分〜1時間
- 1日の実行回数: 最大3回

### タイムライン

| 日数 | 実行回数 | 処理人数 | 累計 | 進捗率 |
|------|----------|----------|------|--------|
| 1日目 | 3回 | 30人 | 60/186 | 32% |
| 2日目 | 3回 | 30人 | 90/186 | 48% |
| 3日目 | 3回 | 30人 | 120/186 | 65% |
| 4日目 | 3回 | 30人 | 150/186 | 81% |
| 5日目 | 3回 | 30人 | 180/186 | 97% |
| 6日目 | 1回 | 6人 | 186/186 | 100% |
| **合計** | **16回** | **156人** | **186/186** | **100%** |

**リトライ**: 7日目（失敗した10人程度）

**総所要時間**: 約7日間

---

## ⚠️ リスク管理

### 高リスク
- **IP制限**: 短時間の大量アクセスで24時間制限
  - **対策**: 実行間隔を30分以上空ける
  
- **ボット検知**: 連続失敗が3回以上
  - **対策**: 即座に中止し、翌日再開

### 中リスク
- **ChromeDriverクラッシュ**: プロセスが残留
  - **対策**: 各実行前にプロセスをクリーンアップ

### 低リスク
- **ネットワークエラー**: 一時的な接続不良
  - **対策**: リトライ機能で自動回復

---

## ✅ 成功の基準

### データ取得完了の条件
- [ ] 186人中180人以上のデータ取得完了（97%以上）
- [ ] 総予想数9,000件以上
- [ ] 重賞予想数500件以上
- [ ] 高信頼度予想家20人以上

### 次のフェーズへの移行条件
- [ ] データ品質チェック完了
- [ ] FAILED_PREDICTORS.md更新完了
- [ ] GitHubにコミット&プッシュ完了
- [ ] PLAYWRIGHT_MIGRATION.md確認済み

---

## 🎯 Phase 4への準備

### データ取得完了後、Phase 4開始前に実施すること

1. **Playwrightへの移行**（2-3日）
   - 環境構築
   - コード書き換え
   - テスト実行

2. **データ品質の最終確認**（半日）
   - 的中率の妥当性チェック
   - 払戻金の妥当性チェック
   - 重複データの確認

3. **ドキュメント整理**（半日）
   - README.md更新
   - CURRENT_STATUS.md更新
   - APIドキュメント準備

**推定**: データ取得完了後、Phase 4開始まで約1週間

---

## 📞 サポート情報

### トラブル発生時

1. **ログを確認**: `logs/scraper_*.log`
2. **データベースを確認**: 進捗確認コマンド実行
3. **プロセスを確認**: `tasklist | findstr chrome`
4. **このドキュメントを参照**: OPTION_A_GUIDE.md

### 質問・相談

新しいチャットで以下のドキュメントをアップロード：
- CURRENT_STATUS.md
- FAILED_PREDICTORS.md
- README.md

---

## 🎉 まとめ

選択肢A（Selenium改善）で着実にデータを取得し、完了後にPlaywrightへ移行する戦略は、以下の理由で最適です：

1. **リスク分散**: 既存コードを活用しつつ改善
2. **学習機会**: Seleniumの問題点を理解した上でPlaywright移行
3. **段階的移行**: Phase 4開始前に最新技術へ移行

---

**次のアクション**: OPTION_A_GUIDE.mdを開いて、ステップ1から実行開始！🚀
