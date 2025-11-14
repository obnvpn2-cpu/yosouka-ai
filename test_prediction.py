"""
予想データ取得のテストスクリプト
"""
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.scraper.prediction import PredictionScraper
from backend.config import settings
import json

def test_prediction_scraper():
    """予想データの取得をテスト"""
    scraper = PredictionScraper()
    scraper.login()
    
    # テスト用予想家ID（キムラヨウヘイ）
    predictor_id = 284
    
    print(f"Testing predictor ID: {predictor_id}")
    print("Fetching predictions...")
    
    predictions = scraper.get_predictor_predictions(predictor_id, limit=5)
    
    print(f"\nFound {len(predictions)} predictions")
    
    if predictions:
        print("\n=== First prediction ===")
        first = predictions[0]
        for key, value in first.items():
            print(f"{key}: {value}")
        
        print("\n=== All predictions (JSON) ===")
        print(json.dumps(predictions, indent=2, default=str))
    else:
        print("No predictions found!")

if __name__ == "__main__":
    test_prediction_scraper()
