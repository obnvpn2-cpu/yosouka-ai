#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
race_idの形式確認
netkeibaのレース詳細ページURLを構築できるか確認
"""
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database import SessionLocal
from backend.models.database import Race


def check_race_id_format():
    """race_idの形式を確認"""
    db = SessionLocal()
    
    print("\n" + "=" * 80)
    print(" race_id 形式の確認")
    print("=" * 80)
    
    # サンプルを取得
    races = db.query(Race).limit(20).all()
    
    print(f"\nrace_idのサンプル（20件）:")
    print(f"\n{'race_id':<20} {'race_name':<30} {'venue':<10} {'date':<12}")
    print("-" * 80)
    
    for race in races:
        race_date = race.race_date.strftime('%Y-%m-%d') if race.race_date else '-'
        print(f"{race.race_id:<20} {race.race_name[:30]:<30} {race.venue:<10} {race_date:<12}")
    
    # race_idの形式分析
    print(f"\n" + "=" * 80)
    print(" race_id 形式の分析")
    print("=" * 80)
    
    race_id_types = {}
    
    for race in db.query(Race).all():
        race_id = race.race_id
        
        # 形式を判定
        if race_id.startswith('temp_'):
            # temp_形式（スクレイピング時に仮作成）
            format_type = "temp（仮ID）"
        elif race_id.isdigit() and len(race_id) == 12:
            # 12桁の数字（netkeibaの標準形式）
            format_type = "netkeiba標準（12桁）"
        elif race_id.isdigit():
            # その他の数字
            format_type = f"数字（{len(race_id)}桁）"
        else:
            # その他
            format_type = "その他"
        
        race_id_types[format_type] = race_id_types.get(format_type, 0) + 1
    
    print(f"\nrace_idの形式別件数:")
    for format_type, count in sorted(race_id_types.items(), key=lambda x: -x[1]):
        print(f"  {format_type}: {count:,}件 ({count/len(db.query(Race).all())*100:.1f}%)")
    
    # temp_形式のサンプル
    temp_races = db.query(Race).filter(Race.race_id.like('temp_%')).limit(5).all()
    if temp_races:
        print(f"\n" + "=" * 80)
        print(" temp_形式のrace_idサンプル")
        print("=" * 80)
        print(f"\n⚠️ これらは仮IDのため、netkeibaのレース詳細ページにアクセスできません")
        print(f"\n{'race_id':<30} {'race_name':<40}")
        print("-" * 80)
        for race in temp_races:
            print(f"{race.race_id:<30} {race.race_name[:40]}")
    
    # netkeiba標準形式のサンプル
    standard_races = [r for r in db.query(Race).limit(100).all() 
                     if r.race_id.isdigit() and len(r.race_id) == 12]
    if standard_races:
        print(f"\n" + "=" * 80)
        print(" netkeiba標準形式のrace_idサンプル")
        print("=" * 80)
        print(f"\n✅ これらはnetkeibaのレース詳細ページにアクセス可能")
        print(f"\n{'race_id':<15} {'URL':<65}")
        print("-" * 80)
        for race in standard_races[:5]:
            url = f"https://race.netkeiba.com/race/result.html?race_id={race.race_id}"
            print(f"{race.race_id:<15} {url}")
    
    # まとめ
    print(f"\n" + "=" * 80)
    print(" 結論")
    print("=" * 80)
    
    total_races = db.query(Race).count()
    temp_count = race_id_types.get("temp（仮ID）", 0)
    standard_count = race_id_types.get("netkeiba標準（12桁）", 0)
    
    print(f"\n総レース数: {total_races:,}件")
    print(f"  temp_形式（仮ID）: {temp_count:,}件 ({temp_count/total_races*100:.1f}%)")
    print(f"  netkeiba標準形式: {standard_count:,}件 ({standard_count/total_races*100:.1f}%)")
    
    if temp_count > 0:
        print(f"\n⚠️ 問題発見:")
        print(f"  temp_形式が{temp_count}件あります")
        print(f"  これらは仮IDのため、レース詳細ページにアクセスできません")
        print(f"\n対策:")
        print(f"  1. netkeibaのレース検索APIを使う")
        print(f"  2. race_nameとrace_dateから実際のrace_idを検索")
        print(f"  3. 予想家ページに戻ってrace_idを再取得")
    
    if standard_count > 0:
        print(f"\n✅ スクレイピング可能:")
        print(f"  {standard_count}件はnetkeibaの標準race_idです")
        print(f"  これらはレース詳細ページから情報を取得できます")
        print(f"\n推奨URL形式:")
        if standard_races:
            print(f"  https://race.netkeiba.com/race/result.html?race_id={standard_races[0].race_id}")
    
    print()
    
    db.close()


if __name__ == "__main__":
    try:
        check_race_id_format()
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
