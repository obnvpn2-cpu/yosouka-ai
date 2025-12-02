#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
残り94件のJSONファイルを詳しく確認
data_intro全体やテーブルデータから情報を抽出できるか調査
"""
import json
from pathlib import Path

json_dir = Path("data/race_details")

# サンプルとして最初の3つを確認
sample_race_ids = [
    "202306030311",  # ダービー卿ＣＴ(G3)
    "202508030511",  # 第68回MBS賞スワンS
    "202508031011",  # 第30回KBSファンタジーS
]

print("=" * 60)
print("残り94件のJSONファイル詳細確認")
print("=" * 60)

for race_id in sample_race_ids:
    json_file = json_dir / f"race_{race_id}_details.json"
    
    print(f"\nrace_id: {race_id}")
    print("-" * 60)
    
    if not json_file.exists():
        print("❌ JSONファイルが存在しません")
        continue
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 全キーを確認
    print("【JSONのキー】")
    for key in data.keys():
        print(f"  - {key}")
    
    # race_infoの詳細
    print("\n【race_info】")
    race_info = data.get('race_info', {})
    for key, value in race_info.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: {value[:100]}...")
        else:
            print(f"  {key}: {value}")
    
    # race_resultsの有無
    print("\n【race_results】")
    race_results = data.get('race_results', [])
    print(f"  レース結果データ: {len(race_results)}頭")
    
    if race_results:
        # 最初の1頭のデータを確認
        print(f"  サンプル（1頭目）:")
        for key, value in race_results[0].items():
            print(f"    {key}: {value}")
    
    print("\n" + "=" * 60)

print("\n確認完了")
