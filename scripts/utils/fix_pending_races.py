#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSONファイルのrace_nameから track_type と distance を再抽出してDB更新
"""
import json
import re
import sqlite3
from pathlib import Path

db_path = "data/keiba.db"
json_dir = Path("data/race_details")

print("=" * 60)
print("JSONのrace_nameから情報を再抽出してDB更新")
print("=" * 60)

# DBから未取得レースのrace_idを取得
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT race_id
    FROM races
    WHERE track_type = '不明' OR track_type IS NULL
""")

pending_race_ids = [row[0] for row in cursor.fetchall()]
print(f"\n未取得レース: {len(pending_race_ids)}件")
print("-" * 60)

success_count = 0
skip_count = 0
error_count = 0

for i, race_id in enumerate(pending_race_ids, 1):
    json_file = json_dir / f"race_{race_id}_details.json"
    
    if not json_file.exists():
        skip_count += 1
        continue
    
    try:
        # JSONファイルを読み込み
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        race_info = data.get('race_info', {})
        race_name = race_info.get('race_name', '')
        
        # race_nameから芝/ダートと距離を抽出
        # パターン1: "芝右 外1200m"
        # パターン2: "ダ右1400m"
        # パターン3: "芝1600m"
        
        track_type = None
        distance = 0
        
        # 芝の検出
        if '芝' in race_name:
            track_type = '芝'
        # ダートの検出（「ダ」または「ダート」）
        elif 'ダ' in race_name or 'ダート' in race_name:
            track_type = 'ダート'
        
        # 距離の抽出（数字 + m のパターン）
        distance_match = re.search(r'(\d+)m', race_name)
        if distance_match:
            distance = int(distance_match.group(1))
        
        # 取得できた場合のみDB更新
        if track_type and distance > 0:
            # 既存の情報を取得
            venue = race_info.get('venue', '不明')
            track_condition = race_info.get('track_condition')
            horse_count = race_info.get('horse_count', 0)
            
            # horse_countが0の場合、race_resultsから取得
            if horse_count == 0:
                race_results = data.get('race_results', [])
                horse_count = len(race_results)
            
            # DB更新
            cursor.execute("""
                UPDATE races
                SET 
                    venue = ?,
                    distance = ?,
                    track_type = ?,
                    track_condition = ?,
                    horse_count = ?
                WHERE race_id = ?
            """, (
                venue,
                distance,
                track_type,
                track_condition,
                horse_count,
                race_id
            ))
            
            if cursor.rowcount > 0:
                success_count += 1
                if success_count <= 10:
                    print(f"[{i}/{len(pending_race_ids)}] ✅ 更新: {race_id}")
                    print(f"   track_type: {track_type}, distance: {distance}m")
                    print(f"   race_name: {race_name[:60]}...")
            
            # 10件ごとにコミット
            if i % 10 == 0:
                conn.commit()
        else:
            error_count += 1
            if error_count <= 5:
                print(f"[{i}/{len(pending_race_ids)}] ❌ 抽出失敗: {race_id}")
                print(f"   track_type: {track_type}, distance: {distance}")
                print(f"   race_name: {race_name[:80]}")
    
    except Exception as e:
        error_count += 1
        if error_count <= 5:
            print(f"[{i}/{len(pending_race_ids)}] ❌ エラー: {race_id} - {e}")
        continue

# 最終コミット
conn.commit()

print("-" * 60)
print(f"\n処理完了")
print("=" * 60)
print(f"処理件数: {len(pending_race_ids)}件")
print(f"成功: {success_count}件")
print(f"スキップ（JSONなし）: {skip_count}件")
print(f"エラー: {error_count}件")
print("=" * 60)

# 更新後の統計を確認
cursor.execute("SELECT COUNT(*) FROM races WHERE track_type IS NOT NULL AND track_type != '不明'")
completed = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM races")
total = cursor.fetchone()[0]

print(f"\n【更新後の状態】")
print(f"総レース数: {total}件")
print(f"詳細取得済み: {completed}件 ({completed/total*100:.1f}%)")
print(f"詳細未取得: {total - completed}件 ({(total - completed)/total*100:.1f}%)")

# 残りの未取得レースを確認
if total - completed > 0:
    print(f"\n【残りの未取得レース（サンプル）】")
    cursor.execute("""
        SELECT race_id, race_name, race_date
        FROM races
        WHERE track_type = '不明' OR track_type IS NULL
        ORDER BY race_date
        LIMIT 5
    """)
    
    for race_id, race_name, race_date in cursor.fetchall():
        print(f"  {race_id} | {race_name} | {race_date}")

conn.close()

print("\n" + "=" * 60)
print("完了")
print("=" * 60)
