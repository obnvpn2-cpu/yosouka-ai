#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
データをCSVファイルにエクスポート
Excel等で開いて詳細に確認できる
"""
import sys
import os
import csv
from datetime import datetime

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database import SessionLocal
from backend.models.database import Predictor, Prediction, Race


def export_predictors():
    """予想家データをCSV出力"""
    db = SessionLocal()
    
    predictors = db.query(Predictor).filter(
        Predictor.total_predictions > 0
    ).order_by(Predictor.total_predictions.desc()).all()
    
    filename = f"exports/predictors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs('exports', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', '名前', '総予想数', '重賞予想数', '信頼度'
        ])
        
        for p in predictors:
            writer.writerow([
                p.netkeiba_id,
                p.name,
                p.total_predictions,
                p.grade_race_predictions,
                p.data_reliability
            ])
    
    print(f"✅ 予想家データを出力: {filename}")
    print(f"   {len(predictors)}人のデータ")
    
    db.close()
    return filename


def export_predictions():
    """予想データをCSV出力"""
    db = SessionLocal()
    
    predictions = db.query(Prediction).join(
        Predictor, Prediction.predictor_id == Predictor.id
    ).join(
        Race, Prediction.race_id == Race.id
    ).order_by(Race.race_date.desc()).limit(1000).all()
    
    filename = f"exports/predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs('exports', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            '予想家ID', '予想家名', 'レース名', '開催日', '競馬場', 
            'グレード', '的中', '払戻金'
        ])
        
        for pred in predictions:
            predictor = db.query(Predictor).filter(
                Predictor.id == pred.predictor_id
            ).first()
            race = db.query(Race).filter(Race.id == pred.race_id).first()
            
            race_date = race.race_date.strftime('%Y-%m-%d') if race.race_date else ''
            hit = '○' if pred.is_hit else ('×' if pred.is_hit == False else '')
            
            writer.writerow([
                predictor.netkeiba_id,
                predictor.name,
                race.race_name,
                race_date,
                race.venue,
                race.grade or '',
                hit,
                pred.payout or 0
            ])
    
    print(f"✅ 予想データを出力: {filename}")
    print(f"   {len(predictions)}件のデータ（最新1000件）")
    
    db.close()
    return filename


def export_grade_races():
    """重賞レースの予想のみをCSV出力"""
    db = SessionLocal()
    
    predictions = db.query(Prediction).join(
        Predictor, Prediction.predictor_id == Predictor.id
    ).join(
        Race, Prediction.race_id == Race.id
    ).filter(
        Race.grade != None
    ).order_by(Race.race_date.desc()).all()
    
    filename = f"exports/grade_races_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs('exports', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            '予想家ID', '予想家名', 'レース名', '開催日', '競馬場', 
            'グレード', '的中', '払戻金'
        ])
        
        for pred in predictions:
            predictor = db.query(Predictor).filter(
                Predictor.id == pred.predictor_id
            ).first()
            race = db.query(Race).filter(Race.id == pred.race_id).first()
            
            race_date = race.race_date.strftime('%Y-%m-%d') if race.race_date else ''
            hit = '○' if pred.is_hit else ('×' if pred.is_hit == False else '')
            
            writer.writerow([
                predictor.netkeiba_id,
                predictor.name,
                race.race_name,
                race_date,
                race.venue,
                race.grade,
                hit,
                pred.payout or 0
            ])
    
    print(f"✅ 重賞予想データを出力: {filename}")
    print(f"   {len(predictions)}件のデータ")
    
    db.close()
    return filename


def export_summary():
    """サマリー統計をCSV出力"""
    db = SessionLocal()
    
    predictors = db.query(Predictor).filter(
        Predictor.total_predictions > 0
    ).all()
    
    filename = f"exports/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs('exports', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            '予想家ID', '予想家名', '総予想数', '的中数', '的中率%', 
            '重賞予想数', '重賞的中数', '重賞的中率%', '総払戻金', '信頼度'
        ])
        
        for predictor in predictors:
            # 的中数を計算
            total_hits = db.query(Prediction).filter(
                Prediction.predictor_id == predictor.id,
                Prediction.is_hit == True
            ).count()
            
            hit_rate = (total_hits / predictor.total_predictions * 100) if predictor.total_predictions > 0 else 0
            
            # 重賞的中数
            grade_hits = db.query(Prediction).join(
                Race, Prediction.race_id == Race.id
            ).filter(
                Prediction.predictor_id == predictor.id,
                Race.grade != None,
                Prediction.is_hit == True
            ).count()
            
            grade_hit_rate = (grade_hits / predictor.grade_race_predictions * 100) if predictor.grade_race_predictions > 0 else 0
            
            # 総払戻金
            total_payout = db.query(func.sum(Prediction.payout)).filter(
                Prediction.predictor_id == predictor.id
            ).scalar() or 0
            
            writer.writerow([
                predictor.netkeiba_id,
                predictor.name,
                predictor.total_predictions,
                total_hits,
                f"{hit_rate:.1f}",
                predictor.grade_race_predictions,
                grade_hits,
                f"{grade_hit_rate:.1f}",
                total_payout,
                predictor.data_reliability
            ])
    
    print(f"✅ サマリー統計を出力: {filename}")
    print(f"   {len(predictors)}人のデータ")
    
    db.close()
    return filename


def main():
    print("\n" + "=" * 80)
    print(" データCSVエクスポート")
    print("=" * 80)
    
    from sqlalchemy import func
    
    try:
        print("\n1. 予想家データ...")
        export_predictors()
        
        print("\n2. 予想データ（最新1000件）...")
        export_predictions()
        
        print("\n3. 重賞予想データ...")
        export_grade_races()
        
        print("\n4. サマリー統計...")
        export_summary()
        
        print("\n" + "=" * 80)
        print(" エクスポート完了")
        print("=" * 80)
        print("\nexports/ フォルダにCSVファイルが生成されました。")
        print("Excelで開いて確認できます。")
        print()
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
