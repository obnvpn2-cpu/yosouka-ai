#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
取得データの詳細確認スクリプト
データベースの内容を分かりやすく表示
"""
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database import SessionLocal
from backend.models.database import Predictor, Prediction, Race
from sqlalchemy import func, distinct
from datetime import datetime


def print_section(title):
    """セクションヘッダーを表示"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def check_database_overview():
    """データベース全体の概要"""
    print_section("データベース概要")
    
    db = SessionLocal()
    
    # 基本統計
    total_predictors = db.query(Predictor).count()
    active_predictors = db.query(Predictor).filter(Predictor.total_predictions > 0).count()
    total_predictions = db.query(Prediction).count()
    total_races = db.query(Race).count()
    
    print(f"\n予想家:")
    print(f"  登録数: {total_predictors}人")
    print(f"  データあり: {active_predictors}人 ({active_predictors/total_predictors*100:.1f}%)")
    print(f"  データなし: {total_predictors - active_predictors}人")
    
    print(f"\n予想:")
    print(f"  総数: {total_predictions:,}件")
    print(f"  予想家あたり平均: {total_predictions/active_predictors:.1f}件")
    
    print(f"\nレース:")
    print(f"  総数: {total_races:,}件")
    
    db.close()


def check_predictors_sample():
    """予想家テーブルのサンプル"""
    print_section("予想家テーブル（サンプル10件）")
    
    db = SessionLocal()
    
    # 予想数が多い順にTOP 10
    predictors = db.query(Predictor).filter(
        Predictor.total_predictions > 0
    ).order_by(Predictor.total_predictions.desc()).limit(10).all()
    
    print(f"\n{'ID':<6} {'名前':<20} {'総予想':<8} {'重賞予想':<8} {'信頼度':<8}")
    print("-" * 80)
    
    for p in predictors:
        print(f"{p.netkeiba_id:<6} {p.name:<20} {p.total_predictions:<8} "
              f"{p.grade_race_predictions:<8} {p.data_reliability:<8}")
    
    db.close()


def check_predictions_sample():
    """予想テーブルのサンプル"""
    print_section("予想テーブル（サンプル10件）")
    
    db = SessionLocal()
    
    # ランダムに10件取得
    predictions = db.query(Prediction).join(
        Predictor, Prediction.predictor_id == Predictor.id
    ).join(
        Race, Prediction.race_id == Race.id
    ).order_by(Prediction.id.desc()).limit(10).all()
    
    print(f"\n{'予想家':<15} {'レース名':<25} {'的中':<6} {'払戻金':<10}")
    print("-" * 80)
    
    for pred in predictions:
        predictor = db.query(Predictor).filter(Predictor.id == pred.predictor_id).first()
        race = db.query(Race).filter(Race.id == pred.race_id).first()
        
        hit = "○" if pred.is_hit else "×"
        payout = f"{pred.payout:,}円" if pred.payout else "-"
        
        print(f"{predictor.name[:15]:<15} {race.race_name[:25]:<25} "
              f"{hit:<6} {payout:<10}")
    
    db.close()


def check_races_sample():
    """レーステーブルのサンプル"""
    print_section("レーステーブル（重賞のみ10件）")
    
    db = SessionLocal()
    
    # 重賞レースのみ
    races = db.query(Race).filter(
        Race.grade != None
    ).order_by(Race.race_date.desc()).limit(10).all()
    
    print(f"\n{'レース名':<30} {'開催日':<12} {'競馬場':<10} {'グレード':<8}")
    print("-" * 80)
    
    for race in races:
        race_date = race.race_date.strftime('%Y-%m-%d') if race.race_date else '-'
        print(f"{race.race_name[:30]:<30} {race_date:<12} "
              f"{race.venue[:10]:<10} {race.grade or '-':<8}")
    
    db.close()


def check_hit_statistics():
    """的中データの統計"""
    print_section("的中データ統計")
    
    db = SessionLocal()
    
    # 的中数
    total_hits = db.query(Prediction).filter(Prediction.is_hit == True).count()
    total_misses = db.query(Prediction).filter(Prediction.is_hit == False).count()
    total_unknown = db.query(Prediction).filter(Prediction.is_hit == None).count()
    
    print(f"\n的中状況:")
    print(f"  的中: {total_hits:,}件 ({total_hits/(total_hits+total_misses+total_unknown)*100:.1f}%)")
    print(f"  不的中: {total_misses:,}件 ({total_misses/(total_hits+total_misses+total_unknown)*100:.1f}%)")
    print(f"  不明: {total_unknown:,}件")
    
    # 払戻金の統計
    payout_stats = db.query(
        func.count(Prediction.id),
        func.min(Prediction.payout),
        func.max(Prediction.payout),
        func.avg(Prediction.payout)
    ).filter(
        Prediction.payout > 0
    ).first()
    
    if payout_stats[0] > 0:
        print(f"\n払戻金統計（的中のみ）:")
        print(f"  件数: {payout_stats[0]:,}件")
        print(f"  最小: {payout_stats[1]:,}円")
        print(f"  最大: {payout_stats[2]:,}円")
        print(f"  平均: {payout_stats[3]:,.0f}円")
    
    db.close()


def check_grade_statistics():
    """重賞データの統計"""
    print_section("重賞データ統計")
    
    db = SessionLocal()
    
    # グレード別の集計
    grade_stats = db.query(
        Race.grade,
        func.count(Prediction.id).label('count')
    ).join(
        Prediction, Race.id == Prediction.race_id
    ).filter(
        Race.grade != None
    ).group_by(Race.grade).all()
    
    print(f"\nグレード別予想数:")
    total_grade = 0
    for grade, count in sorted(grade_stats):
        print(f"  {grade}: {count:,}件")
        total_grade += count
    print(f"  合計: {total_grade:,}件")
    
    # 重賞の的中率
    grade_hits = db.query(func.count(Prediction.id)).join(
        Race, Prediction.race_id == Race.id
    ).filter(
        Race.grade != None,
        Prediction.is_hit == True
    ).scalar()
    
    if total_grade > 0:
        print(f"\n重賞全体の的中率: {grade_hits/total_grade*100:.1f}%")
    
    db.close()


def check_data_quality():
    """データ品質チェック"""
    print_section("データ品質チェック")
    
    db = SessionLocal()
    
    # 1. 的中なのに払戻0のデータ
    hit_no_payout = db.query(Prediction).filter(
        Prediction.is_hit == True,
        Prediction.payout == 0
    ).count()
    
    print(f"\n⚠️ 的中だが払戻金0: {hit_no_payout}件")
    if hit_no_payout > 0:
        print("   → 未来のレースまたはデータ不完全の可能性")
    
    # 2. レース名が不明
    no_race_name = db.query(Race).filter(
        (Race.race_name == None) | (Race.race_name == '')
    ).count()
    
    print(f"⚠️ レース名なし: {no_race_name}件")
    
    # 3. 予想が極端に少ない予想家
    low_predictions = db.query(Predictor).filter(
        Predictor.total_predictions > 0,
        Predictor.total_predictions < 10
    ).count()
    
    print(f"⚠️ 予想数10件未満の予想家: {low_predictions}人")
    print("   → 信頼性が低いため、分析から除外を検討")
    
    # 4. 重賞予想が少ない予想家
    low_grade = db.query(Predictor).filter(
        Predictor.total_predictions > 0,
        Predictor.grade_race_predictions < 5
    ).count()
    
    print(f"⚠️ 重賞予想5件未満の予想家: {low_grade}人")
    print("   → 重賞ランキングから除外を検討")
    
    # 5. 未来のレース
    future_races = db.query(Prediction).join(
        Race, Prediction.race_id == Race.id
    ).filter(
        Race.race_date > datetime.now()
    ).count()
    
    print(f"⚠️ 未来のレース予想: {future_races}件")
    if future_races > 0:
        print("   → 分析時は除外する必要あり")
    
    db.close()


def check_top_predictors():
    """TOP予想家の詳細（簡易版）"""
    print_section("TOP 5 予想家（予想数順）")
    
    db = SessionLocal()
    
    top_predictors = db.query(Predictor).filter(
        Predictor.total_predictions > 0
    ).order_by(Predictor.total_predictions.desc()).limit(5).all()
    
    for i, predictor in enumerate(top_predictors, 1):
        print(f"\n{i}. {predictor.name} (ID: {predictor.netkeiba_id})")
        print(f"   総予想数: {predictor.total_predictions}件")
        print(f"   重賞予想: {predictor.grade_race_predictions}件")
        print(f"   信頼度: {predictor.data_reliability}")
        
        # この予想家の的中数を取得
        hits = db.query(Prediction).filter(
            Prediction.predictor_id == predictor.id,
            Prediction.is_hit == True
        ).count()
        
        if predictor.total_predictions > 0:
            hit_rate = hits / predictor.total_predictions * 100
            print(f"   的中率: {hit_rate:.1f}% ({hits}/{predictor.total_predictions})")
        
        # 払戻金の合計
        total_payout = db.query(func.sum(Prediction.payout)).filter(
            Prediction.predictor_id == predictor.id,
            Prediction.payout > 0
        ).scalar() or 0
        
        print(f"   総払戻: {total_payout:,}円")
    
    db.close()


def main():
    """メイン処理"""
    print("\n" + "=" * 80)
    print(" 取得データ確認レポート")
    print("=" * 80)
    print(f"\n実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 各種チェックを実行
        check_database_overview()
        check_predictors_sample()
        check_predictions_sample()
        check_races_sample()
        check_hit_statistics()
        check_grade_statistics()
        check_data_quality()
        check_top_predictors()
        
        print("\n" + "=" * 80)
        print(" レポート完了")
        print("=" * 80)
        print("\n次のステップ:")
        print("  1. データ品質の問題を確認")
        print("  2. 必要に応じてデータクリーニング")
        print("  3. Phase 4（分析機能）の実装開始")
        print()
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
