#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSONファイルからデータベースを更新するスクリプト
既存のJSONファイル（989件）を読み込んでDBに反映
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# 設定
json_dir = Path("data/race_details")
db_path = "data/keiba.db"

print("=" * 60)
print("JSONファイルからDB更新")
print("=" * 60)

# JSONファイル一覧を取得
json_files = list(json_dir.glob("race_*.json"))
print(f"JSONファイル数: {len(json_files)}件")

if not json_files:
    print("JSONファイルが見つかりません")
    exit(1)

# データベース接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 統計
success_count = 0
skip_count = 0
error_count = 0
not_found_count = 0

print(f"\n処理開始...")
print("-" * 60)

for i, json_file in enumerate(json_files, 1):
    try:
        # JSONファイルを読み込み
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        race_id = data.get('race_id')
        race_info = data.get('race_info', {})
        
        if not race_id or not race_info:
            error_count += 1
            print(f"[{i}/{len(json_files)}] ❌ エラー: {json_file.name} - race_id or race_info not found")
            continue
        
        # DBにrace_idが存在するか確認
        cursor.execute("SELECT id, track_type FROM races WHERE race_id = ?", (race_id,))
        result = cursor.fetchone()
        
        if not result:
            not_found_count += 1
            if not_found_count <= 5:  # 最初の5件だけ表示
                print(f"[{i}/{len(json_files)}] ⚠️  スキップ: {race_id} - DBに存在しません")
            continue
        
        db_id, current_track_type = result
        
        # すでに更新済みか確認
        if current_track_type and current_track_type != '不明':
            skip_count += 1
            continue
        
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
            race_info.get('venue', '不明'),
            race_info.get('distance', 0),
            race_info.get('track_type', '不明'),
            race_info.get('track_condition'),
            race_info.get('horse_count', 0),
            race_id
        ))
        
        if cursor.rowcount > 0:
            success_count += 1
            if success_count <= 10 or success_count % 100 == 0:  # 最初の10件と100件ごと
                print(f"[{i}/{len(json_files)}] ✅ 更新: {race_id} - {race_info.get('track_type')} {race_info.get('distance')}m")
        
        # 100件ごとにコミット
        if i % 100 == 0:
            conn.commit()
            print(f"  → {i}件処理済み（成功: {success_count}, スキップ: {skip_count}, エラー: {error_count}, 未登録: {not_found_count}）")
    
    except Exception as e:
        error_count += 1
        print(f"[{i}/{len(json_files)}] ❌ エラー: {json_file.name} - {e}")
        continue

# 最終コミット
conn.commit()

print("-" * 60)
print(f"\n処理完了")
print("=" * 60)
print(f"処理件数: {len(json_files)}件")
print(f"成功: {success_count}件")
print(f"スキップ（既に更新済み）: {skip_count}件")
print(f"エラー: {error_count}件")
print(f"DBに未登録: {not_found_count}件")
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

conn.close()

print("\n" + "=" * 60)
print("完了")
print("=" * 60)
