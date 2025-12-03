#!/usr/bin/env python3
"""
Phase 4.2: 条件指定検索機能
ユーザーが指定した条件に基づいて、おすすめの予想家を検索
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys

# 最小予想数（固定値）
MIN_PREDICTIONS = 5

def search_predictors(
    venue: Optional[str] = None,
    track_type: Optional[str] = None,
    distances: Optional[List[int]] = None,
    grade: Optional[str] = None,
    sort_by: str = 'hit_rate',
    limit: int = 50
) -> pd.DataFrame:
    """
    条件指定による予想家検索
    
    Args:
        venue: 競馬場（例: '東京', '京都', '中山'）
        track_type: コース種別（'芝', 'ダート'）
        distances: 距離のリスト（例: [1600, 2000]）
        grade: グレード（'G1', 'G2', 'G3', 'オープン', '一般'）
        sort_by: ソート基準（'hit_rate', 'roi'）
        limit: 取得件数
    
    Returns:
        pd.DataFrame: 条件に合致する予想家リスト
    """
    
    db_path = Path('data/keiba.db')
    
    if not db_path.exists():
        print("❌ エラー: data/keiba.db が見つかりません")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    
    # WHERE句を構築
    where_clauses = []
    params = []
    
    if venue:
        where_clauses.append("r.venue = ?")
        params.append(venue)
    
    if track_type:
        where_clauses.append("r.track_type = ?")
        params.append(track_type)
    
    if distances:
        # 複数の距離をORで結合
        distance_placeholders = ','.join(['?'] * len(distances))
        where_clauses.append(f"r.distance IN ({distance_placeholders})")
        params.extend(distances)
    
    if grade:
        if grade in ['G1', 'G2', 'G3']:
            where_clauses.append("r.grade = ?")
            params.append(grade)
        elif grade == 'オープン':
            where_clauses.append("r.is_grade_race = 1")
        elif grade == '一般':
            where_clauses.append("(r.is_grade_race = 0 OR r.is_grade_race IS NULL)")
    
    # WHERE句を結合
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # ソート基準
    order_by = "hit_rate DESC" if sort_by == 'hit_rate' else "avg_roi DESC"
    
    # クエリ実行
    query = f"""
    SELECT 
        pred.id as predictor_id,
        pred.name as predictor_name,
        pred.netkeiba_id,
        COUNT(*) as prediction_count,
        SUM(CASE WHEN p.is_hit = 1 THEN 1 ELSE 0 END) as hit_count,
        ROUND(AVG(CASE WHEN p.is_hit = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as hit_rate,
        SUM(CASE WHEN p.payout IS NOT NULL THEN p.payout ELSE 0 END) as total_payout,
        ROUND(AVG(CASE WHEN p.payout IS NOT NULL THEN p.payout ELSE 0 END), 0) as avg_payout,
        COUNT(CASE WHEN p.roi IS NOT NULL THEN 1 END) as roi_count,
        ROUND(AVG(CASE WHEN p.roi IS NOT NULL THEN p.roi ELSE NULL END), 2) as avg_roi
    FROM predictors pred
    JOIN predictions p ON pred.id = p.predictor_id
    JOIN races r ON p.race_id = r.id
    WHERE {where_sql}
      AND p.is_hit IS NOT NULL
    GROUP BY pred.id
    HAVING prediction_count >= ?
    ORDER BY {order_by}
    LIMIT ?
    """
    
    params.extend([MIN_PREDICTIONS, limit])
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df


def display_search_results(
    df: pd.DataFrame,
    conditions: Dict[str, Any]
):
    """
    検索結果を表示
    
    Args:
        df: 検索結果のDataFrame
        conditions: 検索条件
    """
    
    print("=" * 70)
    print("🔍 条件指定検索結果")
    print("=" * 70)
    print()
    
    # 検索条件を表示
    print("【検索条件】")
    if conditions.get('venue'):
        print(f"  競馬場: {conditions['venue']}")
    if conditions.get('track_type'):
        print(f"  コース種別: {conditions['track_type']}")
    if conditions.get('distances'):
        distances_str = ', '.join([f"{d}m" for d in conditions['distances']])
        print(f"  距離: {distances_str}")
    if conditions.get('grade'):
        print(f"  グレード: {conditions['grade']}")
    print(f"  最小予想数: {MIN_PREDICTIONS}件以上")
    print()
    
    # 結果サマリー
    print("【結果サマリー】")
    print(f"  該当予想家数: {len(df)}人")
    if len(df) > 0:
        print(f"  平均的中率: {df['hit_rate'].mean():.2f}%")
        print(f"  最高的中率: {df['hit_rate'].max():.2f}%")
        print(f"  総予想数: {df['prediction_count'].sum():,}件")
    print()
    
    if len(df) == 0:
        print("⚠️  条件に合致する予想家が見つかりませんでした")
        print("    条件を緩めて再度検索してください")
        return
    
    # TOP3（的中率順）
    print("【的中率TOP3】")
    print()
    top3_hit = df.nlargest(3, 'hit_rate')
    for idx, row in top3_hit.iterrows():
        rank = list(top3_hit.index).index(idx) + 1
        print(f"{rank}. {row['predictor_name']}")
        print(f"   的中率: {row['hit_rate']:.1f}% ({row['hit_count']}/{row['prediction_count']})")
        if row['roi_count'] > 0:
            print(f"   平均ROI: {row['avg_roi']:.1f}%")
        print()
    
    # TOP3（回収率順）- ROIデータがある場合
    df_with_roi = df[df['roi_count'] > 0]
    if len(df_with_roi) >= 3:
        print("【回収率(ROI)TOP3】")
        print()
        top3_roi = df_with_roi.nlargest(3, 'avg_roi')
        for idx, row in top3_roi.iterrows():
            rank = list(top3_roi.index).index(idx) + 1
            print(f"{rank}. {row['predictor_name']}")
            print(f"   平均ROI: {row['avg_roi']:.1f}%")
            print(f"   的中率: {row['hit_rate']:.1f}% ({row['hit_count']}/{row['prediction_count']})")
            print()
    
    # 全体リスト（上位20件）
    print("【該当予想家リスト（上位20件）】")
    print()
    display_df = df.head(20)
    
    for idx, row in display_df.iterrows():
        rank = list(display_df.index).index(idx) + 1
        print(f"{rank:2d}. {row['predictor_name']}")
        print(f"    予想数: {row['prediction_count']}件 | "
              f"的中率: {row['hit_rate']:.1f}% | "
              f"的中数: {row['hit_count']}件")
        if row['roi_count'] > 0:
            print(f"    平均ROI: {row['avg_roi']:.1f}% | "
                  f"平均払戻: {row['avg_payout']:.0f}円")
        print()
    
    if len(df) > 20:
        print(f"... 他 {len(df) - 20}人")
    
    print("=" * 70)


def get_available_options():
    """
    利用可能な検索条件の選択肢を取得
    
    Returns:
        dict: 各条件の選択肢
    """
    
    db_path = Path('data/keiba.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    options = {}
    
    # 競馬場
    cursor.execute("""
        SELECT DISTINCT venue 
        FROM races 
        WHERE venue IS NOT NULL AND venue != '不明'
        ORDER BY venue
    """)
    options['venues'] = [row[0] for row in cursor.fetchall()]
    
    # コース種別
    cursor.execute("""
        SELECT DISTINCT track_type 
        FROM races 
        WHERE track_type IS NOT NULL AND track_type != '不明'
        ORDER BY track_type
    """)
    options['track_types'] = [row[0] for row in cursor.fetchall()]
    
    # 距離
    cursor.execute("""
        SELECT DISTINCT distance 
        FROM races 
        WHERE distance IS NOT NULL AND distance > 0
        ORDER BY distance
    """)
    options['distances'] = [row[0] for row in cursor.fetchall()]
    
    # グレード
    options['grades'] = ['G1', 'G2', 'G3', 'オープン', '一般']
    
    conn.close()
    
    return options


# デモ用実行
if __name__ == "__main__":
    print("=" * 70)
    print("Phase 4.2: 条件指定検索機能デモ")
    print("=" * 70)
    print()
    
    # 利用可能な選択肢を取得
    print("【利用可能な検索条件】")
    options = get_available_options()
    
    print(f"競馬場: {', '.join(options['venues'][:10])}...")
    print(f"コース種別: {', '.join(options['track_types'])}")
    print(f"距離: {', '.join([str(d) for d in options['distances'][:15]])}...")
    print(f"グレード: {', '.join(options['grades'])}")
    print(f"最小予想数: {MIN_PREDICTIONS}件（固定）")
    print()
    
    # デモ検索1: 東京競馬場の芝1600m
    print("\n" + "=" * 70)
    print("【デモ検索1】東京競馬場の芝1600m")
    print("=" * 70)
    conditions1 = {
        'venue': '東京',
        'track_type': '芝',
        'distances': [1600]
    }
    df1 = search_predictors(**conditions1)
    display_search_results(df1, conditions1)
    
    # デモ検索2: 中山競馬場のダート1200m or 1800m、G1のみ
    print("\n" + "=" * 70)
    print("【デモ検索2】中山競馬場のダート1200m/1800m、G1のみ")
    print("=" * 70)
    conditions2 = {
        'venue': '中山',
        'track_type': 'ダート',
        'distances': [1200, 1800],
        'grade': 'G1'
    }
    df2 = search_predictors(**conditions2)
    display_search_results(df2, conditions2)
    
    # デモ検索3: 京都競馬場、芝、G1〜G3（重賞全般）
    print("\n" + "=" * 70)
    print("【デモ検索3】京都競馬場、芝、重賞全般")
    print("=" * 70)
    conditions3 = {
        'venue': '京都',
        'track_type': '芝',
        'grade': 'オープン'
    }
    df3 = search_predictors(**conditions3)
    display_search_results(df3, conditions3)
