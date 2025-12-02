#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
データベースの状態を詳しく確認するスクリプト
"""
import sqlite3
from pathlib import Path

db_path = "data/keiba.db"

print("=" * 60)
print("データベース状態の詳細確認")
print("=" * 60)
print(f"データベースパス: {db_path}")
print(f"ファイル存在: {Path(db_path).exists()}")
if Path(db_path).exists():
    print(f"ファイルサイズ: {Path(db_path).stat().st_size / 1024 / 1024:.2f} MB")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 総レース数
    cursor.execute("SELECT COUNT(*) FROM races")
    total_races = cursor.fetchone()[0]
    print(f"\n【総レース数】")
    print(f"総レース数: {total_races}件")
    
    # 2. track_typeの分布
    print(f"\n【track_typeの分布】")
    cursor.execute("""
        SELECT track_type, COUNT(*) as count
        FROM races
        GROUP BY track_type
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        track_type = row[0] if row[0] else 'NULL'
        count = row[1]
        print(f"  {track_type}: {count}件 ({count/total_races*100:.1f}%)")
    
    # 3. 詳細取得済み（track_typeが'不明'でないもの）
    cursor.execute("""
        SELECT COUNT(*) FROM races 
        WHERE track_type IS NOT NULL AND track_type != '不明'
    """)
    completed = cursor.fetchone()[0]
    print(f"\n【詳細取得状況】")
    print(f"取得済み: {completed}件 ({completed/total_races*100:.1f}%)")
    print(f"未取得: {total_races - completed}件 ({(total_races - completed)/total_races*100:.1f}%)")
    
    # 4. 未取得レースのサンプル（最初の10件）
    print(f"\n【未取得レースのサンプル（最初の10件）】")
    cursor.execute("""
        SELECT race_id, race_name, race_date, track_type, distance
        FROM races
        WHERE track_type = '不明' OR track_type IS NULL
        ORDER BY race_date
        LIMIT 10
    """)
    print(f"{'race_id':<15} {'race_name':<20} {'race_date':<12} {'track_type':<10} {'distance'}")
    print("-" * 80)
    for row in cursor.fetchall():
        race_id = row[0] if row[0] else 'NULL'
        race_name = row[1] if row[1] else 'NULL'
        race_date = row[2] if row[2] else 'NULL'
        track_type = row[3] if row[3] else 'NULL'
        distance = row[4] if row[4] else 0
        print(f"{race_id:<15} {race_name:<20} {race_date:<12} {track_type:<10} {distance}")
    
    # 5. JSONファイルの存在確認
    print(f"\n【JSONファイルの確認】")
    json_dir = Path("data/race_details")
    if json_dir.exists():
        json_files = list(json_dir.glob("race_*.json"))
        print(f"JSONファイル数: {len(json_files)}件")
        
        # 最新のJSONファイルを確認
        if json_files:
            latest_json = max(json_files, key=lambda p: p.stat().st_mtime)
            print(f"最新のJSONファイル: {latest_json.name}")
            
            import json
            with open(latest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\nサンプルJSONの内容:")
            print(f"  race_id: {data.get('race_id')}")
            if 'race_info' in data:
                print(f"  race_name: {data['race_info'].get('race_name')}")
                print(f"  venue: {data['race_info'].get('venue')}")
                print(f"  track_type: {data['race_info'].get('track_type')}")
                print(f"  distance: {data['race_info'].get('distance')}")
    else:
        print(f"JSONディレクトリが存在しません: {json_dir}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("確認完了")
    print("=" * 60)

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
