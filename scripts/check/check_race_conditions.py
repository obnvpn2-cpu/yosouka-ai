#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
レース条件データの状況確認
venue, distance, track_type などの分布を確認
"""
import sys
import os
import re
from collections import Counter

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database import SessionLocal
from backend.models.database import Race


def check_venue_data():
    """競馬場データの確認"""
    db = SessionLocal()
    
    print("\n" + "=" * 80)
    print(" 競馬場（venue）データの状況")
    print("=" * 80)
    
    # venue の分布
    venues = db.query(Race.venue).all()
    venue_counts = Counter([v[0] for v in venues if v[0]])
    
    print(f"\n登録されている競馬場:")
    for venue, count in venue_counts.most_common():
        print(f"  {venue}: {count}件")
    
    # "不明"の数
    unknown = venue_counts.get('不明', 0)
    total = len(venues)
    
    print(f"\n統計:")
    print(f"  総レース数: {total}件")
    print(f"  不明: {unknown}件 ({unknown/total*100:.1f}%)")
    print(f"  判明: {total - unknown}件 ({(total-unknown)/total*100:.1f}%)")
    
    db.close()


def check_distance_data():
    """距離データの確認"""
    db = SessionLocal()
    
    print("\n" + "=" * 80)
    print(" 距離（distance）データの状況")
    print("=" * 80)
    
    # distance の分布
    distances = db.query(Race.distance).all()
    distance_counts = Counter([d[0] for d in distances if d[0] is not None])
    
    # 0の数
    zero_count = sum(1 for d in distances if d[0] == 0 or d[0] is None)
    total = len(distances)
    
    print(f"\n距離の分布（TOP 10）:")
    for distance, count in distance_counts.most_common(10):
        if distance > 0:
            print(f"  {distance}m: {count}件")
    
    print(f"\n統計:")
    print(f"  総レース数: {total}件")
    print(f"  0または NULL: {zero_count}件 ({zero_count/total*100:.1f}%)")
    print(f"  判明: {total - zero_count}件 ({(total-zero_count)/total*100:.1f}%)")
    
    db.close()


def check_track_type_data():
    """トラックタイプデータの確認"""
    db = SessionLocal()
    
    print("\n" + "=" * 80)
    print(" トラック（track_type）データの状況")
    print("=" * 80)
    
    # track_type の分布
    tracks = db.query(Race.track_type).all()
    track_counts = Counter([t[0] for t in tracks if t[0]])
    
    print(f"\n登録されているトラック:")
    for track, count in track_counts.most_common():
        print(f"  {track}: {count}件")
    
    # "不明"の数
    unknown = track_counts.get('不明', 0)
    total = len(tracks)
    
    print(f"\n統計:")
    print(f"  総レース数: {total}件")
    print(f"  不明: {unknown}件 ({unknown/total*100:.1f}%)")
    print(f"  判明: {total - unknown}件 ({(total-unknown)/total*100:.1f}%)")
    
    db.close()


def check_race_name_patterns():
    """race_nameから情報抽出できるか確認"""
    db = SessionLocal()
    
    print("\n" + "=" * 80)
    print(" race_nameからの情報抽出可能性")
    print("=" * 80)
    
    # サンプルを取得
    races = db.query(Race).limit(20).all()
    
    print(f"\nrace_nameのサンプル（20件）:")
    print(f"\n{'race_name':<50} {'抽出可能':<20}")
    print("-" * 80)
    
    for race in races:
        if not race.race_name:
            continue
        
        extractable = []
        
        # 競馬場
        venues = ['東京', '中山', '京都', '阪神', '中京', '新潟', 
                  '小倉', '福島', '札幌', '函館']
        if any(v in race.race_name for v in venues):
            extractable.append('競馬場')
        
        # 距離
        if re.search(r'\d{4}m', race.race_name):
            extractable.append('距離')
        
        # トラック
        if '芝' in race.race_name or 'ダート' in race.race_name or 'ダ' in race.race_name:
            extractable.append('トラック')
        
        # グレード
        if re.search(r'G[123]', race.race_name):
            extractable.append('グレード')
        
        extract_info = ', '.join(extractable) if extractable else '-'
        
        print(f"{race.race_name[:50]:<50} {extract_info:<20}")
    
    db.close()


def extract_info_from_race_name(race_name: str) -> dict:
    """race_nameから情報を抽出（テスト）"""
    info = {}
    
    # 競馬場
    venues = ['東京', '中山', '京都', '阪神', '中京', '新潟', 
              '小倉', '福島', '札幌', '函館']
    for venue in venues:
        if venue in race_name:
            info['venue'] = venue
            break
    
    # 距離
    distance_match = re.search(r'(\d{4})m', race_name)
    if distance_match:
        info['distance'] = int(distance_match.group(1))
    
    # トラック
    if '芝' in race_name:
        info['track_type'] = '芝'
    elif 'ダート' in race_name or 'ダ' in race_name:
        info['track_type'] = 'ダート'
    
    # グレード
    grade_match = re.search(r'G([123])', race_name)
    if grade_match:
        info['grade'] = f"G{grade_match.group(1)}"
    
    return info


def test_extraction():
    """情報抽出のテスト"""
    db = SessionLocal()
    
    print("\n" + "=" * 80)
    print(" 情報抽出テスト（サンプル10件）")
    print("=" * 80)
    
    races = db.query(Race).limit(10).all()
    
    success_count = 0
    total_count = 0
    
    for race in races:
        if not race.race_name:
            continue
        
        total_count += 1
        extracted = extract_info_from_race_name(race.race_name)
        
        print(f"\nレース名: {race.race_name}")
        print(f"  現在のDB: venue={race.venue}, distance={race.distance}, track={race.track_type}")
        print(f"  抽出結果: {extracted}")
        
        if len(extracted) >= 2:  # 2つ以上の情報が取れればOK
            success_count += 1
    
    if total_count > 0:
        print(f"\n抽出成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    db.close()


def analyze_extractability():
    """全データに対する抽出可能性の分析"""
    db = SessionLocal()
    
    print("\n" + "=" * 80)
    print(" 全データに対する抽出可能性分析")
    print("=" * 80)
    
    races = db.query(Race).all()
    
    venue_extractable = 0
    distance_extractable = 0
    track_extractable = 0
    grade_extractable = 0
    total = len(races)
    
    for race in races:
        if not race.race_name:
            continue
        
        extracted = extract_info_from_race_name(race.race_name)
        
        if 'venue' in extracted:
            venue_extractable += 1
        if 'distance' in extracted:
            distance_extractable += 1
        if 'track_type' in extracted:
            track_extractable += 1
        if 'grade' in extracted:
            grade_extractable += 1
    
    print(f"\n総レース数: {total}件")
    print(f"\nrace_nameから抽出可能:")
    print(f"  競馬場: {venue_extractable}件 ({venue_extractable/total*100:.1f}%)")
    print(f"  距離: {distance_extractable}件 ({distance_extractable/total*100:.1f}%)")
    print(f"  トラック: {track_extractable}件 ({track_extractable/total*100:.1f}%)")
    print(f"  グレード: {grade_extractable}件 ({grade_extractable/total*100:.1f}%)")
    
    db.close()


def main():
    print("\n" + "=" * 80)
    print(" レース条件データ状況確認")
    print("=" * 80)
    
    try:
        # 現在のデータ状況
        check_venue_data()
        check_distance_data()
        check_track_type_data()
        
        # race_nameからの抽出可能性
        check_race_name_patterns()
        test_extraction()
        analyze_extractability()
        
        print("\n" + "=" * 80)
        print(" 結論と推奨事項")
        print("=" * 80)
        print("\n次のステップ:")
        print("  1. 上記の結果を確認")
        print("  2. データ補完が必要か判断")
        print("     - 「不明」や「0」が多い → race_nameから抽出")
        print("     - データが十分 → そのまま分析開始")
        print("  3. 条件別分析エンジンの実装")
        print()
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
