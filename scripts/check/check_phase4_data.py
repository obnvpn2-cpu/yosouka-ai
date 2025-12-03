#!/usr/bin/env python3
"""
Phase 4用データ確認スクリプト
データ分析に必要なデータが揃っているか確認
"""

import sqlite3
import sys
from pathlib import Path

def check_phase4_data():
    """Phase 4に必要なデータを確認"""
    
    db_path = Path('data/keiba.db')
    
    if not db_path.exists():
        print("❌ エラー: data/keiba.db が見つかりません")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("Phase 4 データ確認レポート")
    print("=" * 70)
    print()
    
    # 1. 予想家データ
    print("【1. 予想家データ】")
    cursor.execute("SELECT COUNT(*) FROM predictors")
    predictor_count = cursor.fetchone()[0]
    print(f"  予想家数: {predictor_count}人")
    
    cursor.execute("""
        SELECT data_reliability, COUNT(*) 
        FROM predictors 
        GROUP BY data_reliability
    """)
    for reliability, count in cursor.fetchall():
        print(f"    - {reliability}: {count}人")
    print()
    
    # 2. 予想データ
    print("【2. 予想データ】")
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]
    print(f"  総予想数: {total_predictions:,}件")
    
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE is_hit IS NOT NULL")
    predictions_with_result = cursor.fetchone()[0]
    print(f"  結果あり: {predictions_with_result:,}件 ({predictions_with_result/total_predictions*100:.1f}%)")
    
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE is_hit = 1")
    hit_count = cursor.fetchone()[0]
    if predictions_with_result > 0:
        hit_rate = hit_count / predictions_with_result * 100
        print(f"  的中数: {hit_count:,}件 (的中率: {hit_rate:.1f}%)")
    
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE roi IS NOT NULL")
    predictions_with_roi = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(roi) FROM predictions WHERE roi IS NOT NULL")
    avg_roi = cursor.fetchone()[0]
    if predictions_with_roi > 0:
        print(f"  ROIあり: {predictions_with_roi:,}件 (平均ROI: {avg_roi:.1f}%)")
    print()
    
    # 3. レースデータ
    print("【3. レースデータ】")
    cursor.execute("SELECT COUNT(*) FROM races")
    total_races = cursor.fetchone()[0]
    print(f"  総レース数: {total_races}件")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM races 
        WHERE track_type IS NOT NULL AND track_type != '不明'
    """)
    races_with_detail = cursor.fetchone()[0]
    print(f"  詳細あり: {races_with_detail}件 ({races_with_detail/total_races*100:.1f}%)")
    
    # コース種別
    cursor.execute("""
        SELECT track_type, COUNT(*) 
        FROM races 
        WHERE track_type IS NOT NULL AND track_type != '不明'
        GROUP BY track_type
    """)
    print(f"\n  コース種別:")
    for track_type, count in cursor.fetchall():
        print(f"    - {track_type}: {count}件")
    
    # グレード
    cursor.execute("""
        SELECT grade, COUNT(*) 
        FROM races 
        WHERE is_grade_race = 1 
        GROUP BY grade 
        ORDER BY grade
    """)
    print(f"\n  重賞:")
    total_grade_races = 0
    for grade, count in cursor.fetchall():
        print(f"    - {grade}: {count}件")
        total_grade_races += count
    print(f"    合計: {total_grade_races}件")
    print()
    
    # 4. 分析可能性チェック
    print("【4. 分析可能性チェック】")
    
    # 予想家ごとの予想数
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT predictor_id) as predictor_count,
            MIN(prediction_count) as min_predictions,
            MAX(prediction_count) as max_predictions,
            AVG(prediction_count) as avg_predictions
        FROM (
            SELECT predictor_id, COUNT(*) as prediction_count
            FROM predictions
            WHERE is_hit IS NOT NULL
            GROUP BY predictor_id
        )
    """)
    row = cursor.fetchone()
    if row:
        print(f"  結果ありの予想家数: {row[0]}人")
        print(f"  予想数: 最小{row[1]}件 / 平均{row[2]:.0f}件 / 最大{row[3]}件")
    
    # 分析可能な予想家（10件以上）
    cursor.execute("""
        SELECT COUNT(DISTINCT predictor_id)
        FROM predictions
        WHERE is_hit IS NOT NULL
        GROUP BY predictor_id
        HAVING COUNT(*) >= 10
    """)
    analyzable_predictors = len(cursor.fetchall())
    print(f"  分析可能な予想家（10件以上）: {analyzable_predictors}人")
    
    # レース詳細と予想の紐付け確認
    cursor.execute("""
        SELECT COUNT(DISTINCT p.id)
        FROM predictions p
        JOIN races r ON p.race_id = r.id
        WHERE r.track_type IS NOT NULL 
          AND r.track_type != '不明'
          AND p.is_hit IS NOT NULL
    """)
    predictions_with_race_detail = cursor.fetchone()[0]
    print(f"  レース詳細と紐付く予想: {predictions_with_race_detail:,}件")
    
    print()
    
    # 5. Phase 4実装の準備状況
    print("【5. Phase 4実装の準備状況】")
    
    if predictor_count == 0:
        print("  ❌ 予想家データなし")
        ready = False
    else:
        print(f"  ✅ 予想家データあり ({predictor_count}人)")
        ready = True
    
    if predictions_with_result == 0:
        print("  ❌ 結果ありの予想データなし")
        ready = False
    else:
        print(f"  ✅ 結果ありの予想データあり ({predictions_with_result:,}件)")
    
    if races_with_detail == 0:
        print("  ❌ レース詳細データなし")
        ready = False
    else:
        print(f"  ✅ レース詳細データあり ({races_with_detail}件)")
    
    if analyzable_predictors == 0:
        print("  ❌ 分析可能な予想家なし（10件以上の予想が必要）")
        ready = False
    else:
        print(f"  ✅ 分析可能な予想家あり ({analyzable_predictors}人)")
    
    print()
    
    if ready:
        print("🎉 Phase 4の実装準備が整いました！")
        print()
        print("次のステップ:")
        print("  1. 基本統計の計算スクリプト作成")
        print("  2. 条件別分析スクリプト作成")
        print("  3. ランキング生成スクリプト作成")
    else:
        print("⚠️  Phase 4の準備が不十分です")
        print("   Phase 2, 3を完了してから再実行してください")
    
    print()
    print("=" * 70)
    
    conn.close()
    
    return ready

if __name__ == "__main__":
    ready = check_phase4_data()
    sys.exit(0 if ready else 1)
