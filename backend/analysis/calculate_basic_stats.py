#!/usr/bin/env python3
"""
Phase 4.1: 基本統計計算スクリプト
予想家ごとの的中率、回収率、その他基本統計を計算
"""

import sqlite3
import pandas as pd
from pathlib import Path
import sys

def calculate_basic_stats():
    """予想家ごとの基本統計を計算"""
    
    db_path = Path('data/keiba.db')
    
    if not db_path.exists():
        print("❌ エラー: data/keiba.db が見つかりません")
        sys.exit(1)
    
    print("=" * 70)
    print("Phase 4.1: 基本統計計算")
    print("=" * 70)
    print()
    
    conn = sqlite3.connect(db_path)
    
    # 予想家ごとの基本統計を計算
    query = """
    SELECT 
        pred.id as predictor_id,
        pred.name as predictor_name,
        pred.netkeiba_id,
        pred.data_reliability,
        COUNT(*) as total_predictions,
        SUM(CASE WHEN p.is_hit = 1 THEN 1 ELSE 0 END) as hit_count,
        ROUND(AVG(CASE WHEN p.is_hit = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as hit_rate,
        SUM(CASE WHEN p.payout IS NOT NULL THEN p.payout ELSE 0 END) as total_payout,
        ROUND(AVG(CASE WHEN p.payout IS NOT NULL THEN p.payout ELSE 0 END), 0) as avg_payout,
        SUM(CASE WHEN p.roi IS NOT NULL THEN 1 ELSE 0 END) as roi_count,
        ROUND(AVG(CASE WHEN p.roi IS NOT NULL THEN p.roi ELSE NULL END), 2) as avg_roi,
        -- 重賞の成績
        SUM(CASE WHEN r.is_grade_race = 1 THEN 1 ELSE 0 END) as grade_predictions,
        SUM(CASE WHEN r.is_grade_race = 1 AND p.is_hit = 1 THEN 1 ELSE 0 END) as grade_hits,
        ROUND(
            AVG(CASE 
                WHEN r.is_grade_race = 1 THEN 
                    CASE WHEN p.is_hit = 1 THEN 1.0 ELSE 0.0 END 
                ELSE NULL 
            END) * 100, 
            2
        ) as grade_hit_rate
    FROM predictors pred
    JOIN predictions p ON pred.id = p.predictor_id
    LEFT JOIN races r ON p.race_id = r.id
    WHERE p.is_hit IS NOT NULL
    GROUP BY pred.id
    HAVING total_predictions >= 10
    ORDER BY hit_rate DESC
    """
    
    print("データベースから統計を計算中...")
    df = pd.read_sql_query(query, conn)
    
    print(f"✅ {len(df)}人の予想家の統計を計算しました")
    print()
    
    # 基本統計のサマリー
    print("【全体サマリー】")
    print(f"  分析対象予想家: {len(df)}人")
    print(f"  総予想数: {df['total_predictions'].sum():,}件")
    print(f"  総的中数: {df['hit_count'].sum():,}件")
    print(f"  平均的中率: {df['hit_rate'].mean():.2f}%")
    print(f"  最高的中率: {df['hit_rate'].max():.2f}%")
    print(f"  最低的中率: {df['hit_rate'].min():.2f}%")
    print()
    
    # 重賞成績のサマリー
    df_with_grade = df[df['grade_predictions'] > 0]
    if len(df_with_grade) > 0:
        print("【重賞成績サマリー】")
        print(f"  重賞予想ありの予想家: {len(df_with_grade)}人")
        print(f"  総重賞予想数: {df_with_grade['grade_predictions'].sum():,}件")
        print(f"  総重賞的中数: {df_with_grade['grade_hits'].sum():,}件")
        print(f"  平均重賞的中率: {df_with_grade['grade_hit_rate'].mean():.2f}%")
        print()
    
    # TOP20予想家を表示
    print("【的中率TOP20】")
    print()
    top20 = df.nlargest(20, 'hit_rate')
    
    for idx, row in top20.iterrows():
        rank = list(top20.index).index(idx) + 1
        print(f"{rank:2d}. {row['predictor_name']}")
        print(f"    的中率: {row['hit_rate']:.1f}% ({row['hit_count']}/{row['total_predictions']})")
        if row['grade_predictions'] > 0:
            print(f"    重賞的中率: {row['grade_hit_rate']:.1f}% ({row['grade_hits']}/{row['grade_predictions']})")
        print()
    
    # CSVとして保存
    output_dir = Path('data/analysis')
    output_dir.mkdir(exist_ok=True)
    
    csv_path = output_dir / 'predictor_basic_stats.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ 統計データを保存しました: {csv_path}")
    
    # データベースにも保存（テーブル作成）
    print()
    print("データベースに統計テーブルを作成中...")
    
    # 既存のテーブルを削除
    conn.execute("DROP TABLE IF EXISTS predictor_stats")
    
    # 新しいテーブルを作成
    conn.execute("""
    CREATE TABLE predictor_stats (
        predictor_id INTEGER PRIMARY KEY,
        predictor_name TEXT,
        netkeiba_id INTEGER,
        data_reliability TEXT,
        total_predictions INTEGER,
        hit_count INTEGER,
        hit_rate REAL,
        total_payout INTEGER,
        avg_payout REAL,
        roi_count INTEGER,
        avg_roi REAL,
        grade_predictions INTEGER,
        grade_hits INTEGER,
        grade_hit_rate REAL,
        FOREIGN KEY (predictor_id) REFERENCES predictors(id)
    )
    """)
    
    # データを挿入
    df.to_sql('predictor_stats', conn, if_exists='replace', index=False)
    
    conn.commit()
    print("✅ データベースに統計テーブル（predictor_stats）を作成しました")
    
    conn.close()
    
    print()
    print("=" * 70)
    print("Phase 4.1 完了！")
    print()
    print("次のステップ:")
    print("  - Phase 4.2: 条件別分析（芝/ダート、距離、競馬場）")
    print("  - Phase 4.3: ランキング生成")
    print("=" * 70)
    
    return df

if __name__ == "__main__":
    df = calculate_basic_stats()
