"""
失敗した予想家の一括リトライスクリプト
"""
import sys
import os

# プロジェクトルートをsys.pathに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.scraper.prediction import PredictionScraper
from backend.database import SessionLocal
from backend.models.database import Predictor, Prediction, Race
from loguru import logger
from datetime import datetime
import time


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
            return 0
        
        for pred_data in predictions_data:
            # レース名がない予想はスキップ
            if not pred_data.get('race_name'):
                logger.debug(f"Skipping prediction with no race_name")
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
                race = Race(
                    race_id=f"temp_{predictor_id}_{pred_data.get('prediction_id', 0)}",
                    race_name=pred_data['race_name'],
                    race_date=pred_data.get('race_date', datetime.utcnow()),
                    venue=pred_data.get('venue', '不明'),
                    grade=pred_data.get('grade'),
                    distance=0,
                    track_type='不明',
                    is_grade_race=pred_data.get('grade') in ['G1', 'G2', 'G3']
                )
                db.add(race)
                db.flush()
            
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
        
        # 予想家の統計を更新
        predictor.total_predictions = db.query(Prediction).filter(
            Prediction.predictor_id == predictor.id
        ).count()
        
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
        return saved_count
        
    except Exception as e:
        logger.error(f"Error saving predictions for predictor {predictor_id}: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def retry_failed_predictors():
    """失敗した予想家をリトライ"""
    
    # 失敗した予想家のIDリスト
    failed_ids = [
        60, 136, 142, 156, 229, 258, 283, 305, 329, 353,
        360, 364, 432, 494, 495, 518, 531, 539, 562, 600,
        601, 627, 638, 660, 680
    ]
    
    logger.info(f"Starting retry for {len(failed_ids)} failed predictors")
    
    # スクレイパーを初期化
    scraper = PredictionScraper()
    scraper.login()
    
    success_count = 0
    fail_count = 0
    
    for i, predictor_id in enumerate(failed_ids, 1):
        # データベースから予想家情報を取得
        db = SessionLocal()
        try:
            predictor = db.query(Predictor).filter(
                Predictor.netkeiba_id == predictor_id
            ).first()
            
            if not predictor:
                logger.warning(f"Predictor {predictor_id} not found in database")
                fail_count += 1
                continue
            
            predictor_name = predictor.name
        finally:
            db.close()
        
        logger.info(f"[{i}/{len(failed_ids)}] Retrying: {predictor_name} (ID: {predictor_id})")
        
        try:
            # 予想履歴を取得
            predictions = scraper.get_predictor_predictions(predictor_id, limit=50)
            
            if predictions:
                saved = save_predictions(predictor_id, predictions)
                if saved > 0:
                    logger.info(f"✅ Success: {predictor_name} - {saved} predictions saved")
                    success_count += 1
                else:
                    logger.warning(f"⚠️ No new predictions: {predictor_name}")
                    fail_count += 1
            else:
                logger.warning(f"❌ Failed: {predictor_name} - No predictions found")
                fail_count += 1
        
        except Exception as e:
            logger.error(f"❌ Error: {predictor_name} - {e}")
            fail_count += 1
        
        # 次の予想家との間隔（アクセス制限対策）
        if i < len(failed_ids):
            logger.debug(f"Waiting 15 seconds before next predictor...")
            time.sleep(15)
    
    # 結果サマリー
    logger.info("\n" + "=" * 70)
    logger.info("Retry Results")
    logger.info("=" * 70)
    logger.info(f"Total attempted: {len(failed_ids)}")
    logger.info(f"✅ Success: {success_count}")
    logger.info(f"❌ Failed: {fail_count}")
    logger.info(f"Success rate: {success_count/len(failed_ids)*100:.1f}%")
    
    # 最終統計
    db = SessionLocal()
    try:
        total = db.query(Predictor).count()
        processed = db.query(Predictor).filter(Predictor.total_predictions > 0).count()
        total_predictions = db.query(Prediction).count()
        
        logger.info("\n" + "=" * 70)
        logger.info("Final Statistics")
        logger.info("=" * 70)
        logger.info(f"Total predictors: {total}")
        logger.info(f"Processed: {processed}/{total} ({processed/total*100:.1f}%)")
        logger.info(f"Total predictions: {total_predictions:,}")
        logger.info("=" * 70)
    finally:
        db.close()


if __name__ == "__main__":
    # ログ設定
    logger.add("logs/retry_{time}.log", rotation="1 day", retention="7 days")
    
    try:
        retry_failed_predictors()
    except KeyboardInterrupt:
        logger.info("Retry interrupted by user")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        # Chromeプロセスを強制終了
        import os
        try:
            os.system("taskkill /F /IM chrome.exe /T 2>nul")
            os.system("taskkill /F /IM chromedriver.exe /T 2>nul")
        except:
            pass
