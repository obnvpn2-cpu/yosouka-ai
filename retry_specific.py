"""
特定の予想家をリトライするスクリプト

使用例:
  python retry_specific.py 60 136 142  # 3人をリトライ
  python retry_specific.py --all       # 失敗した全員をリトライ
"""
import sys
import os
import argparse

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
        
        predictor = db.query(Predictor).filter(
            Predictor.netkeiba_id == predictor_id
        ).first()
        
        if not predictor:
            logger.error(f"Predictor {predictor_id} not found in database")
            return 0
        
        for pred_data in predictions_data:
            if not pred_data.get('race_name'):
                continue
            
            if pred_data.get('prediction_id'):
                existing = db.query(Prediction).filter(
                    Prediction.netkeiba_prediction_id == pred_data['prediction_id']
                ).first()
                
                if existing:
                    continue
            
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
        
        predictor.total_predictions = db.query(Prediction).filter(
            Prediction.predictor_id == predictor.id
        ).count()
        
        predictor.grade_race_predictions = db.query(Prediction).join(Race).filter(
            Prediction.predictor_id == predictor.id,
            Race.is_grade_race == True
        ).count()
        
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


def get_failed_predictors():
    """データベースから失敗した予想家を取得"""
    db = SessionLocal()
    try:
        failed = db.query(Predictor.netkeiba_id, Predictor.name).filter(
            Predictor.total_predictions == 0
        ).order_by(Predictor.netkeiba_id).all()
        return [(nid, name) for nid, name in failed]
    finally:
        db.close()


def retry_predictors(predictor_ids: list):
    """指定された予想家をリトライ"""
    
    logger.info(f"Starting retry for {len(predictor_ids)} predictors")
    
    # 予想家情報を取得
    db = SessionLocal()
    try:
        predictor_info = {}
        for pid in predictor_ids:
            predictor = db.query(Predictor).filter(
                Predictor.netkeiba_id == pid
            ).first()
            if predictor:
                predictor_info[pid] = predictor.name
            else:
                logger.warning(f"Predictor {pid} not found in database")
    finally:
        db.close()
    
    # スクレイパーを初期化
    scraper = PredictionScraper()
    scraper.login()
    
    success_count = 0
    fail_count = 0
    
    for i, predictor_id in enumerate(predictor_ids, 1):
        predictor_name = predictor_info.get(predictor_id, f"ID:{predictor_id}")
        
        logger.info(f"[{i}/{len(predictor_ids)}] Retrying: {predictor_name} (ID: {predictor_id})")
        
        try:
            predictions = scraper.get_predictor_predictions(predictor_id, limit=50)
            
            if predictions:
                saved = save_predictions(predictor_id, predictions)
                if saved > 0:
                    logger.info(f"✅ Success: {predictor_name} - {saved} predictions")
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
        
        if i < len(predictor_ids):
            logger.debug(f"Waiting 15 seconds...")
            time.sleep(15)
    
    # 結果サマリー
    logger.info("\n" + "=" * 70)
    logger.info("Retry Results")
    logger.info("=" * 70)
    logger.info(f"Total: {len(predictor_ids)}")
    logger.info(f"✅ Success: {success_count}")
    logger.info(f"❌ Failed: {fail_count}")
    if len(predictor_ids) > 0:
        logger.info(f"Success rate: {success_count/len(predictor_ids)*100:.1f}%")
    logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='特定の予想家をリトライ')
    parser.add_argument('predictor_ids', nargs='*', type=int, help='予想家のnetkeiba_id')
    parser.add_argument('--all', action='store_true', help='失敗した全予想家をリトライ')
    parser.add_argument('--list', action='store_true', help='失敗した予想家をリスト表示')
    
    args = parser.parse_args()
    
    if args.list:
        # 失敗した予想家をリスト表示
        failed = get_failed_predictors()
        print(f"\n失敗した予想家: {len(failed)}人\n")
        for idx, (nid, name) in enumerate(failed, 1):
            print(f"{idx:2d}. [{nid:4d}] {name}")
        print()
        return
    
    if args.all:
        # 全失敗予想家をリトライ
        failed = get_failed_predictors()
        predictor_ids = [nid for nid, _ in failed]
        logger.info(f"Retrying all {len(predictor_ids)} failed predictors")
    elif args.predictor_ids:
        # 指定されたIDをリトライ
        predictor_ids = args.predictor_ids
    else:
        print("エラー: 予想家IDを指定するか、--all または --list を使用してください")
        print("\n使用例:")
        print("  python retry_specific.py 60 136 142     # 特定の3人をリトライ")
        print("  python retry_specific.py --all          # 失敗した全員をリトライ")
        print("  python retry_specific.py --list         # 失敗した予想家をリスト表示")
        return
    
    retry_predictors(predictor_ids)


if __name__ == "__main__":
    logger.add("logs/retry_{time}.log", rotation="1 day", retention="7 days")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Retry interrupted by user")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        import os
        try:
            os.system("taskkill /F /IM chrome.exe /T 2>nul")
            os.system("taskkill /F /IM chromedriver.exe /T 2>nul")
        except:
            pass
