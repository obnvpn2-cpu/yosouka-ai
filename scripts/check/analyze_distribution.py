#!/usr/bin/env python3
"""
条件別のデータ分布確認スクリプト
各条件でどのくらいの予想データがあるか確認
"""

import sqlite3
import pandas as pd
from pathlib import Path

def analyze_data_distribution():
    """データの分布を分析"""
    
    db_path = Path('data/keiba.db')
    conn = sqlite3.connect(db_path)
    
    print("=" * 70)
    print("データ分布分析")
    print("=" * 70)
    print()
    
    # 1. 競馬場別
    print("【1. 競馬場別の予想数】")
    query1 = """
    SELECT 
        r.venue,
        COUNT(*) as prediction_count,
        COUNT(DISTINCT p.predictor_id) as predictor_count
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    WHERE r.venue IS NOT NULL AND r.venue != '不明'
    GROUP BY r.venue
    ORDER BY prediction_count DESC
    """
    df1 = pd.read_sql_query(query1, conn)
    for _, row in df1.iterrows():
        print(f"  {row['venue']:8s}: 予想{row['prediction_count']:4d}件 | 予想家{row['predictor_count']:3d}人")
    print()
    
    # 2. コース種別×距離
    print("【2. コース種別×距離の予想数（上位20）】")
    query2 = """
    SELECT 
        r.track_type,
        r.distance,
        COUNT(*) as prediction_count,
        COUNT(DISTINCT p.predictor_id) as predictor_count
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    WHERE r.track_type IS NOT NULL 
      AND r.track_type != '不明'
      AND r.distance IS NOT NULL
      AND r.distance > 0
    GROUP BY r.track_type, r.distance
    ORDER BY prediction_count DESC
    LIMIT 20
    """
    df2 = pd.read_sql_query(query2, conn)
    for _, row in df2.iterrows():
        print(f"  {row['track_type']:4s} {row['distance']:4d}m: "
              f"予想{row['prediction_count']:4d}件 | 予想家{row['predictor_count']:3d}人")
    print()
    
    # 3. 競馬場×コース種別
    print("【3. 競馬場×コース種別の予想数（上位20）】")
    query3 = """
    SELECT 
        r.venue,
        r.track_type,
        COUNT(*) as prediction_count,
        COUNT(DISTINCT p.predictor_id) as predictor_count
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    WHERE r.venue IS NOT NULL 
      AND r.venue != '不明'
      AND r.track_type IS NOT NULL 
      AND r.track_type != '不明'
    GROUP BY r.venue, r.track_type
    ORDER BY prediction_count DESC
    LIMIT 20
    """
    df3 = pd.read_sql_query(query3, conn)
    for _, row in df3.iterrows():
        print(f"  {row['venue']:8s} {row['track_type']:4s}: "
              f"予想{row['prediction_count']:4d}件 | 予想家{row['predictor_count']:3d}人")
    print()
    
    # 4. 予想家ごとの最多予想条件
    print("【4. 予想家が10件以上予想している条件の組み合わせ数】")
    query4 = """
    SELECT 
        COUNT(*) as combination_count
    FROM (
        SELECT 
            p.predictor_id,
            r.venue,
            r.track_type,
            COUNT(*) as pred_count
        FROM predictions p
        JOIN races r ON p.race_id = r.id
        WHERE r.venue IS NOT NULL 
          AND r.venue != '不明'
          AND r.track_type IS NOT NULL 
          AND r.track_type != '不明'
        GROUP BY p.predictor_id, r.venue, r.track_type
        HAVING pred_count >= 10
    )
    """
    cursor = conn.cursor()
    cursor.execute(query4)
    count = cursor.fetchone()[0]
    print(f"  10件以上: {count}組み合わせ")
    
    query5 = """
    SELECT 
        COUNT(*) as combination_count
    FROM (
        SELECT 
            p.predictor_id,
            r.venue,
            r.track_type,
            COUNT(*) as pred_count
        FROM predictions p
        JOIN races r ON p.race_id = r.id
        WHERE r.venue IS NOT NULL 
          AND r.venue != '不明'
          AND r.track_type IS NOT NULL 
          AND r.track_type != '不明'
        GROUP BY p.predictor_id, r.venue, r.track_type
        HAVING pred_count >= 5
    )
    """
    cursor.execute(query5)
    count = cursor.fetchone()[0]
    print(f"  5件以上: {count}組み合わせ")
    print()
    
    # 5. グレード別
    print("【5. グレード別の予想数】")
    query6 = """
    SELECT 
        r.grade,
        COUNT(*) as prediction_count,
        COUNT(DISTINCT p.predictor_id) as predictor_count
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    WHERE r.grade IS NOT NULL
    GROUP BY r.grade
    ORDER BY prediction_count DESC
    """
    df6 = pd.read_sql_query(query6, conn)
    for _, row in df6.iterrows():
        print(f"  {row['grade']:4s}: 予想{row['prediction_count']:4d}件 | 予想家{row['predictor_count']:3d}人")
    
    # 重賞全体
    query7 = """
    SELECT 
        COUNT(*) as prediction_count,
        COUNT(DISTINCT p.predictor_id) as predictor_count
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    WHERE r.is_grade_race = 1
    """
    cursor.execute(query7)
    row = cursor.fetchone()
    print(f"  重賞全体: 予想{row[0]:4d}件 | 予想家{row[1]:3d}人")
    print()
    
    # 6. 推奨条件の組み合わせ
    print("【6. 推奨検索パターン（10人以上ヒット）】")
    
    # パターン1: コース種別のみ
    print("\n  パターン1: コース種別のみ")
    query8 = """
    SELECT 
        r.track_type,
        COUNT(DISTINCT p.predictor_id) as predictor_count
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    WHERE r.track_type IN ('芝', 'ダート')
    GROUP BY r.track_type
    HAVING COUNT(*) >= 10
    """
    df8 = pd.read_sql_query(query8, conn)
    for _, row in df8.iterrows():
        print(f"    {row['track_type']}: {row['predictor_count']}人")
    
    # パターン2: 競馬場のみ
    print("\n  パターン2: 競馬場のみ")
    query9 = """
    SELECT 
        r.venue,
        COUNT(DISTINCT p.predictor_id) as predictor_count
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    WHERE r.venue IS NOT NULL AND r.venue != '不明'
    GROUP BY r.venue
    HAVING COUNT(*) >= 10
    ORDER BY predictor_count DESC
    LIMIT 10
    """
    df9 = pd.read_sql_query(query9, conn)
    for _, row in df9.iterrows():
        print(f"    {row['venue']}: {row['predictor_count']}人")
    
    # パターン3: グレードのみ
    print("\n  パターン3: グレードのみ")
    query10 = """
    SELECT 
        CASE 
            WHEN r.is_grade_race = 1 THEN '重賞'
            ELSE '一般'
        END as race_type,
        COUNT(DISTINCT p.predictor_id) as predictor_count
    FROM predictions p
    JOIN races r ON p.race_id = r.id
    GROUP BY race_type
    HAVING COUNT(*) >= 10
    """
    df10 = pd.read_sql_query(query10, conn)
    for _, row in df10.iterrows():
        print(f"    {row['race_type']}: {row['predictor_count']}人")
    
    print()
    print("=" * 70)
    
    conn.close()

if __name__ == "__main__":
    analyze_data_distribution()
