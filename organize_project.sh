#!/bin/bash
# ファイル整理スクリプト
# 実行前にバックアップを取ることを推奨

set -e  # エラーで停止

echo "=================================="
echo "ファイル整理スクリプト"
echo "=================================="
echo ""

# プロジェクトルートに移動
cd ~/デスクトップ/repo/keiba-yosoka-ai

echo "📁 ディレクトリ作成中..."
mkdir -p scripts/batch
mkdir -p scripts/check
mkdir -p scripts/debug
mkdir -p scripts/test
mkdir -p scripts/utils

echo ""
echo "📦 ファイル移動中..."

# 1. バッチ処理スクリプト
echo "  → scripts/batch/"
mv batch_race_detail.py scripts/batch/ 2>/dev/null || echo "    (batch_race_detail.py なし)"
mv batch_update_race_ids.py scripts/batch/ 2>/dev/null || echo "    (batch_update_race_ids.py なし)"
mv batch_update_race_ids_v2.py scripts/batch/ 2>/dev/null || echo "    (batch_update_race_ids_v2.py なし)"
mv batch_all_with_interval.sh scripts/batch/ 2>/dev/null || echo "    (batch_all_with_interval.sh なし)"
mv batch_with_interval.sh scripts/batch/ 2>/dev/null || echo "    (batch_with_interval.sh なし)"

# 2. チェックスクリプト
echo "  → scripts/check/"
mv check_race_progress.py scripts/check/ 2>/dev/null || echo "    (check_race_progress.py なし)"
mv check_db_status.py scripts/check/ 2>/dev/null || echo "    (check_db_status.py なし)"
mv check_data.py scripts/check/ 2>/dev/null || echo "    (check_data.py なし)"
mv check_date_range.py scripts/check/ 2>/dev/null || echo "    (check_date_range.py なし)"
mv check_pending_json.py scripts/check/ 2>/dev/null || echo "    (check_pending_json.py なし)"
mv check_predictor.py scripts/check/ 2>/dev/null || echo "    (check_predictor.py なし)"
mv check_progress.py scripts/check/ 2>/dev/null || echo "    (check_progress.py なし)"
mv check_race_conditions.py scripts/check/ 2>/dev/null || echo "    (check_race_conditions.py なし)"
mv check_race_id.py scripts/check/ 2>/dev/null || echo "    (check_race_id.py なし)"
mv check_results.py scripts/check/ 2>/dev/null || echo "    (check_results.py なし)"

# 3. デバッグスクリプト
echo "  → scripts/debug/"
mv debug_html.py scripts/debug/ 2>/dev/null || echo "    (debug_html.py なし)"
mv debug_html_structure.py scripts/debug/ 2>/dev/null || echo "    (debug_html_structure.py なし)"
mv debug_pandas_html.py scripts/debug/ 2>/dev/null || echo "    (debug_pandas_html.py なし)"

# 4. テストスクリプト
echo "  → scripts/test/"
mv test_fixed_scraper.py scripts/test/ 2>/dev/null || echo "    (test_fixed_scraper.py なし)"
mv test_pandas_scraper.py scripts/test/ 2>/dev/null || echo "    (test_pandas_scraper.py なし)"
mv test_prediction.py scripts/test/ 2>/dev/null || echo "    (test_prediction.py なし)"

# 5. ユーティリティスクリプト
echo "  → scripts/utils/"
mv update_race_ids.py scripts/utils/ 2>/dev/null || echo "    (update_race_ids.py なし)"
mv update_race_ids_v2.py scripts/utils/ 2>/dev/null || echo "    (update_race_ids_v2.py なし)"
mv update_db_from_json.py scripts/utils/ 2>/dev/null || echo "    (update_db_from_json.py なし)"
mv fix_pending_races.py scripts/utils/ 2>/dev/null || echo "    (fix_pending_races.py なし)"
mv inspect_remaining_json.py scripts/utils/ 2>/dev/null || echo "    (inspect_remaining_json.py なし)"
mv export_csv.py scripts/utils/ 2>/dev/null || echo "    (export_csv.py なし)"
mv organize_files.py scripts/utils/ 2>/dev/null || echo "    (organize_files.py なし)"
mv retry_failed.py scripts/utils/ 2>/dev/null || echo "    (retry_failed.py なし)"
mv retry_specific.py scripts/utils/ 2>/dev/null || echo "    (retry_specific.py なし)"
mv race_detail_scraper.py scripts/utils/ 2>/dev/null || echo "    (race_detail_scraper.py なし)"

# 6. ドキュメント
echo "  → docs/"
mv RACE_DETAIL_SCRAPER_GUIDE.md docs/ 2>/dev/null || echo "    (RACE_DETAIL_SCRAPER_GUIDE.md なし)"

echo ""
echo "✅ 整理完了！"
echo ""
echo "📊 整理後の構造:"
echo ""
tree -L 2 -I 'venv|__pycache__|*.pyc|.git|race_details|yosouka-ai' --dirsfirst

echo ""
echo "=================================="
echo "次のステップ:"
echo "1. git status で変更を確認"
echo "2. git add . でステージング"
echo "3. git commit -m 'ファイル整理: scriptsディレクトリに再編成'"
echo "4. git push origin main"
echo "=================================="
