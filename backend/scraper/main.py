"""
メインスクレイピングスクリプト（--limit, --offset対応版）
"""
import sys
import os

# プロジェクトルートをsys.pathに追加（ModuleNotFoundError対策）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.scraper.predictor_list import PredictorListScraper
from backend.scraper.prediction import PredictionScraper
from backend.database import SessionLocal, init_db
from backend.models.database import Predictor, Prediction, Race
from loguru import logger
import argparse
from datetime import datetime


def save_predictors(predictors_data: list):
    """予想家情報をデータベースに保存"""
    db = SessionLocal()
    try:
        saved_count = 0
        for predictor_data in predictors_data:
            # 既存の予想家をチェック
            existing = db.query(Predictor).filter(
                Predictor.netkeiba_id == predictor_data['netkeiba_id']
            ).first()
            
            if existing:
                # 既存の予想家を更新
                existing.name = predictor_data['name']
                existing.updated_at = datetime.utcnow()
                logger.debug(f"Updated predictor: {predictor_data['name']}")
            else:
                # 新規予想家を作成
                predictor = Predictor(
                    netkeiba_id=predictor_data['netkeiba_id'],
                    name=predictor_data['name']
                )
                db.add(predictor)
                saved_count += 1
                logger.debug(f"Created new predictor: {predictor_data['name']}")
        
        db.commit()
        logger.info(f"Saved {saved_count} new predictors to database")
        
    except Exception as e:
        logger.error(f"Error saving predictors: {e}")
        db.rollback()
    finally:
        db.close()


def save_predictions(predictor_id: int, predictions_data: list):
    """予想情報をデータベースに保存"""
    db = SessionLocal()
    try:
        saved_count = 0
        
        # 予想家を取得
        predictor = db.query(Predictor).filter(
            Predictor.netkeiba_id == predictor_id
        ).first()
        
        if not predictor:
            logger.error(f"Predictor {predictor_id} not found in database")
            return
        
        for pred_data in predictions_data:
            # レース名がない予想はスキップ
            if not pred_data.get('race_name'):
                logger.debug(f"Skipping prediction with no race_name: {pred_data.get('prediction_id')}")
                continue
            
            # 既存の予想をチェック
            if pred_data.get('prediction_id'):
                existing = db.query(Prediction).filter(
                    Prediction.netkeiba_prediction_id == pred_data['prediction_id']
                ).first()
                
                if existing:
                    logger.debug(f"Prediction {pred_data['prediction_id']} already exists")
                    continue
            
            # レースを作成または取得
            race = None
            if pred_data.get('race_name'):
                # 簡易的なレース作成（詳細は後で更新可能）
                race = Race(
                    race_id=f"temp_{predictor_id}_{pred_data.get('prediction_id', 0)}",
                    race_name=pred_data['race_name'],
                    race_date=pred_data.get('race_date', datetime.utcnow()),
                    venue=pred_data.get('venue', '不明'),
                    grade=pred_data.get('grade'),
                    distance=0,  # 後で更新
                    track_type='不明',  # 後で更新
                    is_grade_race=pred_data.get('grade') in ['G1', 'G2', 'G3']
                )
                db.add(race)
                db.flush()  # IDを取得
            
            # 予想を作成
            prediction = Prediction(
                predictor_id=predictor.id,
                race_id=race.id if race else None,
                netkeiba_prediction_id=pred_data.get('prediction_id'),
                predicted_at=pred_data.get('race_date', datetime.utcnow()),
                is_hit=pred_data.get('is_hit'),
                payout=pred_data.get('payout')
            )
            
            db.add(prediction)
            saved_count += 1
        
        # 予想家の総予想数を更新
        predictor.total_predictions = db.query(Prediction).filter(
            Prediction.predictor_id == predictor.id
        ).count()
        
        # 重賞予想数を更新
        predictor.grade_race_predictions = db.query(Prediction).join(Race).filter(
            Prediction.predictor_id == predictor.id,
            Race.is_grade_race == True
        ).count()
        
        # 信頼度を更新
        if predictor.grade_race_predictions >= 15:
            predictor.data_reliability = "high"
        elif predictor.grade_race_predictions >= 10:
            predictor.data_reliability = "medium"
        else:
            predictor.data_reliability = "low"
        
        db.commit()
        logger.info(f"Saved {saved_count} predictions for predictor {predictor_id}")
        
    except Exception as e:
        logger.error(f"Error saving predictions for predictor {predictor_id}: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """メイン処理"""
    # 引数パーサーを設定
    parser = argparse.ArgumentParser(description='競馬予想家スクレイピング')
    parser.add_argument('--limit', type=int, default=None, help='処理する予想家の数')
    parser.add_argument('--offset', type=int, default=0, help='開始位置（スキップする予想家の数）')
    parser.add_argument('--test', action='store_true', help='テストモード（最初の5人のみ）')
    
    args = parser.parse_args()
    
    logger.info("Starting scraping process...")
    logger.info(f"Arguments: limit={args.limit}, offset={args.offset}, test={args.test}")
    
    # データベースを初期化（初回のみ）
    try:
        init_db()
    except Exception as e:
        logger.warning(f"Database may already exist: {e}")
    
    # 予想家一覧スクレイパー
    predictor_scraper = PredictorListScraper()
    
    # ログイン（有料会員の場合）
    predictor_scraper.login()
    
    # 予想家一覧を取得
    logger.info("Fetching predictor list...")
    predictors = predictor_scraper.get_all_active_predictors()
    
    if not predictors:
        logger.error("No predictors found. Exiting.")
        return
    
    logger.info(f"Found {len(predictors)} predictors")
    
    # 予想家をデータベースに保存
    save_predictors(predictors)
    
    # 各予想家の予想履歴を取得
    prediction_scraper = PredictionScraper()
    prediction_scraper.login()
    
    # 処理範囲を決定
    if args.test:
        # テストモード：最初の5人
        start_idx = 0
        end_idx = min(5, len(predictors))
        logger.info("Running in TEST mode - processing first 5 predictors only")
    else:
        # 通常モード：offset と limit を使用
        start_idx = args.offset
        if args.limit:
            end_idx = min(start_idx + args.limit, len(predictors))
        else:
            end_idx = len(predictors)
    
    target_predictors = predictors[start_idx:end_idx]
    total_count = len(target_predictors)
    
    logger.info(f"Processing predictors [{start_idx}:{end_idx}] ({total_count} predictors)")
    logger.info(f"Total predictors in list: {len(predictors)}")
    
    for i, predictor_data in enumerate(target_predictors, 1):
        predictor_id = predictor_data['netkeiba_id']
        predictor_name = predictor_data['name']
        actual_index = start_idx + i - 1
        
        logger.info(f"[{i}/{total_count}] [index {actual_index}] Processing: {predictor_name} (ID: {predictor_id})")
        
        # 予想履歴を取得
        predictions = prediction_scraper.get_predictor_predictions(predictor_id, limit=50)
        
        if predictions:
            # データベースに保存
            save_predictions(predictor_id, predictions)
        else:
            logger.warning(f"No predictions found for predictor {predictor_id}")
    
    logger.info("Scraping process completed!")
    logger.info(f"Processed {total_count} predictors [index {start_idx} to {end_idx-1}]")
    
    # 次のoffsetを明示的に表示
    if end_idx < len(predictors):
        logger.info(f"✅ Next offset: {end_idx}")
        logger.info(f"✅ Next command: python backend/scraper/main.py --limit 10 --offset {end_idx}")
        remaining = len(predictors) - end_idx
        logger.info(f"📊 Remaining: {remaining} predictors")
    else:
        logger.info("🎉 All predictors in list have been processed!")
    
    # 統計を表示
    db = SessionLocal()
    try:
        total_predictors = db.query(Predictor).count()
        processed_predictors = db.query(Predictor).filter(Predictor.total_predictions > 0).count()
        total_predictions = db.query(Prediction).count()
        high_reliability = db.query(Predictor).filter(Predictor.data_reliability == "high").count()
        
        logger.info(f"\n=== Statistics ===")
        logger.info(f"Total predictors in DB: {total_predictors}")
        logger.info(f"Processed predictors: {processed_predictors}/{total_predictors}")
        logger.info(f"Total predictions: {total_predictions}")
        logger.info(f"High reliability predictors: {high_reliability}")
        
    finally:
        db.close()


if __name__ == "__main__":
    # ログ設定
    logger.add("logs/scraper_{time}.log", rotation="1 day", retention="7 days")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        # Chromeプロセスを強制終了
        import os
        import signal
        try:
            os.system("taskkill /F /IM chrome.exe /T 2>nul")
            os.system("taskkill /F /IM chromedriver.exe /T 2>nul")
        except:
            pass
        
        # プログラムを明示的に終了
        import sys
        sys.exit(0)
