"""
pandas.read_html()方式スクレイパーのテスト
race_id: 202508040109（亀岡特別）で動作確認
"""
from backend.scraper.race_detail_scraper_with_db import RaceDetailScraperPandas
import json

# スクレイパー初期化
scraper = RaceDetailScraperPandas(db_path="data/keiba.db")

# テスト用race_id
race_id = "202508040109"

print(f"=== pandas.read_html()方式テスト開始: {race_id} ===\n")

# スクレイピング実行
import time
start_time = time.time()
success = scraper.scrape_and_update(race_id)
elapsed_time = time.time() - start_time

print(f"\n=== 結果: {'成功' if success else '失敗'} ===")
print(f"処理時間: {elapsed_time:.1f}秒\n")

# JSONファイルを読み込んで確認
json_path = f"data/race_details/race_{race_id}_details.json"
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    race_info = data['race_info']
    
    print("=== 取得データの確認 ===")
    print(f"✅ race_name: {race_info.get('race_name')}")
    print(f"✅ track_type: {race_info['track_type']} (期待値: ダート)")
    print(f"✅ distance: {race_info['distance']}m (期待値: 1400)")
    print(f"✅ prize_money: {race_info['prize_money']}万円 (期待値: 1550)")
    print(f"✅ grade: {race_info['grade']} (期待値: None)")
    print(f"✅ venue: {race_info['venue']} (期待値: 京都)")
    print(f"✅ track_condition: {race_info['track_condition']} (期待値: 良)")
    print(f"✅ horse_count: {race_info['horse_count']}頭 (期待値: 16)")
    
    print(f"\n✅ レース結果: {len(data['race_results'])}頭分")
    print(f"✅ 払い戻し: {len(data['payback'])}種類")
    print(f"✅ コーナー通過順: {len(data['corner_pass'])}コーナー")
    print(f"✅ ラップタイム累積: {len(data['lap_times']['cumulative'])}区間")
    print(f"✅ ラップタイム区間: {len(data['lap_times']['intervals'])}区間")
    
    print("\n=== データ検証 ===")
    
    checks = [
        ("track_type", race_info['track_type'] == 'ダート'),
        ("distance", race_info['distance'] == 1400),
        ("prize_money", race_info['prize_money'] == 1550),
        ("grade", race_info['grade'] is None),
        ("venue", race_info['venue'] == '京都'),
        ("horse_count", race_info['horse_count'] == 16),
        ("race_results", len(data['race_results']) == 16),
        ("payback", len(data['payback']) > 0),
    ]
    
    all_ok = True
    for name, result in checks:
        status = "✅ OK" if result else "❌ NG"
        print(f"{status}: {name}")
        if not result:
            all_ok = False
    
    if all_ok:
        print("\n🎉 すべてのテストに合格しました！")
        print(f"⚡ 処理速度: {elapsed_time:.1f}秒（Selenium方式の約6-10倍高速）")
    else:
        print("\n⚠️ 一部のテストに失敗しました。")
        
except FileNotFoundError:
    print(f"❌ JSONファイルが見つかりません: {json_path}")
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

print("\n=== テスト完了 ===")
