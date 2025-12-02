#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
個別予想家の詳細データ確認
特定の予想家のデータを詳しく見る
"""
import sys
import os
import argparse

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database import SessionLocal
from backend.models.database import Predictor, Prediction, Race
from datetime import datetime


def show_predictor_detail(predictor_id: int):
    """予想家の詳細データを表示"""
    db = SessionLocal()
    
    # 予想家情報
    predictor = db.query(Predictor).filter(
        Predictor.netkeiba_id == predictor_id
    ).first()
    
    if not predictor:
        print(f"予想家 ID {predictor_id} が見つかりません")
        db.close()
        return
    
    print("\n" + "=" * 80)
    print(f" 予想家詳細: {predictor.name}")
    print("=" * 80)
    print(f"\nID: {predictor.netkeiba_id}")
    print(f"名前: {predictor.name}")
    print(f"総予想数: {predictor.total_predictions}件")
    print(f"重賞予想数: {predictor.grade_race_predictions}件")
    print(f"信頼度: {predictor.data_reliability}")
    
    # 予想リストを取得
    predictions = db.query(Prediction).filter(
        Prediction.predictor_id == predictor.id
    ).join(Race, Prediction.race_id == Race.id).order_by(
        Race.race_date.desc()
    ).all()
    
    if not predictions:
        print("\n予想データがありません")
        db.close()
        return
    
    # 統計
    total = len(predictions)
    hits = sum(1 for p in predictions if p.is_hit)
    misses = sum(1 for p in predictions if p.is_hit == False)
    unknown = total - hits - misses
    
    print(f"\n【統計】")
    print(f"的中: {hits}件 ({hits/total*100:.1f}%)")
    print(f"不的中: {misses}件 ({misses/total*100:.1f}%)")
    print(f"不明: {unknown}件")
    
    # 払戻金
    total_payout = sum(p.payout for p in predictions if p.payout)
    avg_payout = total_payout / hits if hits > 0 else 0
    
    print(f"\n【払戻】")
    print(f"総払戻: {total_payout:,}円")
    print(f"平均払戻: {avg_payout:,.0f}円")
    
    # 重賞のみの統計
    grade_preds = [p for p in predictions if db.query(Race).filter(
        Race.id == p.race_id, Race.grade != None
    ).first()]
    
    if grade_preds:
        grade_hits = sum(1 for p in grade_preds if p.is_hit)
        print(f"\n【重賞成績】")
        print(f"重賞予想: {len(grade_preds)}件")
        print(f"重賞的中: {grade_hits}件 ({grade_hits/len(grade_preds)*100:.1f}%)")
    
    # 最近の予想（10件）
    print(f"\n【最近の予想（10件）】")
    print(f"\n{'日付':<12} {'レース名':<25} {'競馬場':<8} {'グレード':<6} {'的中':<6} {'払戻':<10}")
    print("-" * 80)
    
    for pred in predictions[:10]:
        race = db.query(Race).filter(Race.id == pred.race_id).first()
        
        race_date = race.race_date.strftime('%Y-%m-%d') if race.race_date else '-'
        race_name = race.race_name[:25] if race.race_name else '-'
        venue = race.venue[:8] if race.venue else '-'
        grade = race.grade or '-'
        hit = "○" if pred.is_hit else ("×" if pred.is_hit == False else "?")
        payout = f"{pred.payout:,}円" if pred.payout else "-"
        
        print(f"{race_date:<12} {race_name:<25} {venue:<8} {grade:<6} {hit:<6} {payout:<10}")
    
    # グレード別の成績
    g1_preds = [p for p in predictions if db.query(Race).filter(
        Race.id == p.race_id, Race.grade == 'G1'
    ).first()]
    g2_preds = [p for p in predictions if db.query(Race).filter(
        Race.id == p.race_id, Race.grade == 'G2'
    ).first()]
    g3_preds = [p for p in predictions if db.query(Race).filter(
        Race.id == p.race_id, Race.grade == 'G3'
    ).first()]
    
    if g1_preds or g2_preds or g3_preds:
        print(f"\n【グレード別成績】")
        
        if g1_preds:
            g1_hits = sum(1 for p in g1_preds if p.is_hit)
            print(f"G1: {g1_hits}/{len(g1_preds)}的中 ({g1_hits/len(g1_preds)*100:.1f}%)")
        
        if g2_preds:
            g2_hits = sum(1 for p in g2_preds if p.is_hit)
            print(f"G2: {g2_hits}/{len(g2_preds)}的中 ({g2_hits/len(g2_preds)*100:.1f}%)")
        
        if g3_preds:
            g3_hits = sum(1 for p in g3_preds if p.is_hit)
            print(f"G3: {g3_hits}/{len(g3_preds)}的中 ({g3_hits/len(g3_preds)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    
    db.close()


def list_predictors(limit=20):
    """予想家一覧を表示"""
    db = SessionLocal()
    
    predictors = db.query(Predictor).filter(
        Predictor.total_predictions > 0
    ).order_by(Predictor.total_predictions.desc()).limit(limit).all()
    
    print("\n" + "=" * 80)
    print(f" 予想家一覧（TOP {limit}）")
    print("=" * 80)
    print(f"\n{'ID':<6} {'名前':<20} {'総予想':<8} {'重賞':<6} {'信頼度':<8}")
    print("-" * 80)
    
    for p in predictors:
        print(f"{p.netkeiba_id:<6} {p.name[:20]:<20} {p.total_predictions:<8} "
              f"{p.grade_race_predictions:<6} {p.data_reliability:<8}")
    
    print()
    
    db.close()


def main():
    parser = argparse.ArgumentParser(description='予想家データの詳細確認')
    parser.add_argument('predictor_id', nargs='?', type=int, help='予想家ID')
    parser.add_argument('--list', action='store_true', help='予想家一覧を表示')
    parser.add_argument('--limit', type=int, default=20, help='一覧表示件数')
    
    args = parser.parse_args()
    
    if args.list:
        list_predictors(args.limit)
    elif args.predictor_id:
        show_predictor_detail(args.predictor_id)
    else:
        print("使用方法:")
        print("  python check_predictor.py 60          # ID 60の予想家を表示")
        print("  python check_predictor.py --list      # 予想家一覧を表示")
        print("  python check_predictor.py --list --limit 50  # TOP 50を表示")


if __name__ == "__main__":
    main()
