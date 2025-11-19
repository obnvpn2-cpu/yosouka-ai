#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
データ期間の確認
予想データが実際にどの期間をカバーしているか確認
"""
import sys
import os
from collections import Counter
from datetime import datetime

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database import SessionLocal
from backend.models.database import Race, Prediction


def check_date_range():
    """データの期間を確認"""
    db = SessionLocal()
    
    print("\n" + "=" * 80)
    print(" データ期間の確認")
    print("=" * 80)
    
    # 基本統計
    total_races = db.query(Race).count()
    races_with_date = db.query(Race).filter(Race.race_date != None).count()
    
    print(f"\n【基本情報】")
    print(f"総レース数: {total_races:,}件")
    print(f"日付あり: {races_with_date:,}件 ({races_with_date/total_races*100:.1f}%)")
    
    if races_with_date == 0:
        print("\n⚠️ race_dateが全て NULL です")
        db.close()
        return
    
    # 日付範囲
    oldest = db.query(Race.race_date).filter(
        Race.race_date != None
    ).order_by(Race.race_date.asc()).first()
    
    newest = db.query(Race.race_date).filter(
        Race.race_date != None
    ).order_by(Race.race_date.desc()).first()
    
    print(f"\n【期間】")
    if oldest and oldest[0]:
        print(f"最古のレース: {oldest[0].strftime('%Y年%m月%d日')}")
    if newest and newest[0]:
        print(f"最新のレース: {newest[0].strftime('%Y年%m月%d日')}")
    
    if oldest and newest and oldest[0] and newest[0]:
        days = (newest[0] - oldest[0]).days
        years = days / 365.25
        print(f"期間: {days:,}日間（約{years:.1f}年）")
    
    # 年別の分布
    print(f"\n【年別の分布】")
    races = db.query(Race).filter(Race.race_date != None).all()
    
    year_counts = Counter()
    for race in races:
        if race.race_date:
            year = race.race_date.year
            year_counts[year] += 1
    
    for year in sorted(year_counts.keys()):
        count = year_counts[year]
        bar = "█" * (count // 50)  # 50件で1バー
        print(f"  {year}年: {count:4,}件 {bar}")
    
    # 月別の分布（直近1年）
    print(f"\n【月別の分布（直近1年）】")
    
    month_counts = Counter()
    for race in races:
        if race.race_date:
            # 直近1年のデータのみ
            if newest and newest[0]:
                if (newest[0] - race.race_date).days <= 365:
                    month_key = race.race_date.strftime('%Y-%m')
                    month_counts[month_key] += 1
    
    for month in sorted(month_counts.keys())[-12:]:  # 直近12ヶ月
        count = month_counts[month]
        bar = "█" * (count // 10)  # 10件で1バー
        print(f"  {month}: {count:3,}件 {bar}")
    
    # 未来のレース
    now = datetime.now()
    future_races = db.query(Race).filter(Race.race_date > now).count()
    past_races = db.query(Race).filter(Race.race_date <= now).count()
    
    print(f"\n【過去/未来の分布】")
    print(f"  過去のレース: {past_races:,}件 ({past_races/races_with_date*100:.1f}%)")
    print(f"  未来のレース: {future_races:,}件 ({future_races/races_with_date*100:.1f}%)")
    
    # 競馬場別の期間分析（TOP 5競馬場）
    print(f"\n【主要競馬場別の期間】")
    
    venues = ['東京', '京都', '福島', '中山', '阪神']
    
    for venue in venues:
        venue_races = db.query(Race).filter(
            Race.venue == venue,
            Race.race_date != None
        ).all()
        
        if not venue_races:
            continue
        
        venue_dates = [r.race_date for r in venue_races if r.race_date]
        if venue_dates:
            oldest_venue = min(venue_dates)
            newest_venue = max(venue_dates)
            
            print(f"\n  {venue}競馬場: {len(venue_races)}件")
            print(f"    期間: {oldest_venue.strftime('%Y-%m-%d')} 〜 {newest_venue.strftime('%Y-%m-%d')}")
    
    # 予想数が多い予想家のデータ期間（サンプル5人）
    print(f"\n【予想家別の期間サンプル（TOP 5）】")
    
    from backend.models.database import Predictor
    
    top_predictors = db.query(Predictor).filter(
        Predictor.total_predictions > 0
    ).order_by(Predictor.total_predictions.desc()).limit(5).all()
    
    for predictor in top_predictors:
        predictions = db.query(Prediction).filter(
            Prediction.predictor_id == predictor.id
        ).join(Race, Prediction.race_id == Race.id).all()
        
        race_dates = []
        for pred in predictions:
            race = db.query(Race).filter(Race.id == pred.race_id).first()
            if race and race.race_date:
                race_dates.append(race.race_date)
        
        if race_dates:
            oldest_pred = min(race_dates)
            newest_pred = max(race_dates)
            days_range = (newest_pred - oldest_pred).days
            
            print(f"\n  {predictor.name} ({predictor.total_predictions}件)")
            print(f"    期間: {oldest_pred.strftime('%Y-%m-%d')} 〜 {newest_pred.strftime('%Y-%m-%d')} ({days_range}日間)")
    
    # まとめ
    print(f"\n" + "=" * 80)
    print(" まとめ")
    print("=" * 80)
    
    if oldest and newest and oldest[0] and newest[0]:
        print(f"\n✅ データ期間: {oldest[0].year}年 〜 {newest[0].year}年")
        print(f"✅ 総レース数: {races_with_date:,}件")
        print(f"✅ 過去のレース: {past_races:,}件（分析対象）")
        print(f"✅ 未来のレース: {future_races:,}件（分析対象外）")
        
        print(f"\n【次のステップの判断材料】")
        print(f"スクレイピングすべきレース数: 約{past_races:,}件")
        print(f"推定所要時間: 約{past_races*1.5/3600:.1f}時間（1件1.5秒として）")
    
    print()
    
    db.close()


if __name__ == "__main__":
    try:
        check_date_range()
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
