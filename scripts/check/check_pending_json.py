#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
未取得レースのJSONファイルを確認
"""
import json
import sqlite3
from pathlib import Path

db_path = "data/keiba.db"
json_dir = Path("data/race_details")

print("=" * 60)
print("未取得レースのJSONファイル確認")
print("=" * 60)

# DBから未取得レースのrace_idを取得
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT race_id, race_name, race_date
    FROM races
    WHERE track_type = '不明' OR track_type IS NULL
    ORDER BY race_date
    LIMIT 10
""")

pending_races = cursor.fetchall()
conn.close()

print(f"\n未取得レース（最初の10件）:")
print("-" * 60)

for race_id, race_name, race_date in pending_races:
    print(f"\nrace_id: {race_id}")
    print(f"race_name: {race_name}")
    print(f"race_date: {race_date}")
    
    # 対応するJSONファイルを探す
    json_file = json_dir / f"race_{race_id}_details.json"
    
    if json_file.exists():
        print(f"✅ JSONファイル: 存在")
        
        # JSONの中身を確認
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        race_info = data.get('race_info', {})
        
        print(f"   track_type: {race_info.get('track_type', 'キーなし')}")
        print(f"   distance: {race_info.get('distance', 'キーなし')}")
        print(f"   venue: {race_info.get('venue', 'キーなし')}")
        print(f"   track_condition: {race_info.get('track_condition', 'キーなし')}")
        
        # track_typeが'不明'かチェック
        if race_info.get('track_type') == '不明' or not race_info.get('track_type'):
            print(f"   ⚠️  JSONのtrack_typeが「不明」または空です")
            
            # race_nameを確認（ここから情報が取れるかも）
            print(f"   race_name（JSON）: {race_info.get('race_name', 'なし')[:50]}")
    else:
        print(f"❌ JSONファイル: 存在しない")
    
    print("-" * 60)

print("\n" + "=" * 60)
print("確認完了")
print("=" * 60)
