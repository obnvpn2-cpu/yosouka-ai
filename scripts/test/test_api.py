#!/usr/bin/env python3
"""
API動作確認スクリプト
起動したAPIに対してテストリクエストを送信
"""

import requests
import json

# APIのベースURL
BASE_URL = "http://localhost:8000"

def test_api():
    """APIの動作確認"""
    
    print("=" * 70)
    print("API動作確認テスト")
    print("=" * 70)
    print()
    
    # 1. ヘルスチェック
    print("【1. ヘルスチェック】GET /")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # 2. 統計情報取得
    print("【2. 統計情報】GET /api/stats")
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # 3. 選択肢取得
    print("【3. 検索条件の選択肢】GET /api/options")
    response = requests.get(f"{BASE_URL}/api/options")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"競馬場: {len(data['venues'])}件 - {', '.join(data['venues'][:5])}...")
    print(f"コース種別: {data['track_types']}")
    print(f"距離: {len(data['distances'])}件 - {data['distances'][:10]}...")
    print(f"グレード: {data['grades']}")
    print(f"最小予想数: {data['min_predictions']}件")
    print()
    
    # 4. 検索テスト1: 東京競馬場の芝
    print("【4. 検索テスト1】POST /api/search - 東京競馬場の芝")
    payload = {
        "venue": "東京",
        "track_type": "芝",
        "sort_by": "hit_rate",
        "limit": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"該当予想家数: {data['total_count']}人")
    print(f"平均的中率: {data['avg_hit_rate']:.2f}%")
    print(f"最高的中率: {data['max_hit_rate']:.2f}%")
    print(f"\nTOP5:")
    for i, predictor in enumerate(data['predictors'], 1):
        print(f"  {i}. {predictor['predictor_name']}")
        print(f"     的中率: {predictor['hit_rate']:.1f}% "
              f"({predictor['hit_count']}/{predictor['prediction_count']})")
    print()
    
    # 5. 検索テスト2: 芝1600m
    print("【5. 検索テスト2】POST /api/search - 芝1600m")
    payload = {
        "track_type": "芝",
        "distances": [1600],
        "sort_by": "hit_rate",
        "limit": 3
    }
    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"該当予想家数: {data['total_count']}人")
    print(f"平均的中率: {data['avg_hit_rate']:.2f}%")
    print(f"\nTOP3:")
    for i, predictor in enumerate(data['predictors'], 1):
        print(f"  {i}. {predictor['predictor_name']}")
        print(f"     的中率: {predictor['hit_rate']:.1f}% "
              f"({predictor['hit_count']}/{predictor['prediction_count']})")
    print()
    
    # 6. 検索テスト3: G1のみ
    print("【6. 検索テスト3】POST /api/search - G1のみ")
    payload = {
        "grade": "G1",
        "sort_by": "hit_rate",
        "limit": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"該当予想家数: {data['total_count']}人")
    print(f"平均的中率: {data['avg_hit_rate']:.2f}%")
    print(f"\nTOP5:")
    for i, predictor in enumerate(data['predictors'], 1):
        print(f"  {i}. {predictor['predictor_name']}")
        print(f"     的中率: {predictor['hit_rate']:.1f}% "
              f"({predictor['hit_count']}/{predictor['prediction_count']})")
    print()
    
    print("=" * 70)
    print("✅ APIテスト完了")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ エラー: APIサーバーに接続できません")
        print("   先にAPIサーバーを起動してください:")
        print("   python backend/api/api.py")
    except Exception as e:
        print(f"❌ エラー: {e}")
