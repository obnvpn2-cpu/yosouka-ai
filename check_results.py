#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
リトライ後の結果確認スクリプト
"""
import sqlite3

def check_retry_results():
    """リトライ後の統計を表示"""
    conn = sqlite3.connect('data/keiba.db')
    cursor = conn.cursor()
    
    # 基本統計
    cursor.execute("SELECT COUNT(*) FROM predictors")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
    successful = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM predictions")
    predictions = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM predictions p 
        JOIN races r ON p.race_id = r.id
        WHERE r.grade IS NOT NULL
    """)
    grade_predictions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM predictors WHERE data_reliability = 'high'")
    high_reliability = cursor.fetchone()[0]
    
    # 結果表示
    print("=" * 70)
    print("リトライ後の統計")
    print("=" * 70)
    print(f"\n成功: {successful}/{total}人 ({successful/total*100:.1f}%)")
    print(f"失敗: {total - successful}人 ({(total - successful)/total*100:.1f}%)")
    print(f"\n総予想数: {predictions:,}件")
    print(f"重賞予想: {grade_predictions:,}件 ({grade_predictions/predictions*100:.1f}%)")
    print(f"高信頼度予想家: {high_reliability}人")
    
    # まだ失敗している予想家
    cursor.execute("""
        SELECT netkeiba_id, name 
        FROM predictors 
        WHERE total_predictions = 0
        ORDER BY netkeiba_id
    """)
    still_failed = cursor.fetchall()
    
    if still_failed:
        print(f"\n" + "=" * 70)
        print(f"まだ失敗している予想家: {len(still_failed)}人")
        print("=" * 70)
        for idx, (nid, name) in enumerate(still_failed, 1):
            print(f"{idx:2d}. [{nid:4d}] {name}")
    else:
        print(f"\n" + "=" * 70)
        print("🎉 全予想家のデータ取得完了！")
        print("=" * 70)
    
    # 次のステップ提案
    success_rate = successful / total * 100
    print(f"\n" + "=" * 70)
    print("次のステップ")
    print("=" * 70)
    
    if success_rate >= 95:
        print("✅ 成功率95%以上 - Phase 4（分析機能）へ進むことを推奨")
    elif success_rate >= 90:
        print("✅ 成功率90%以上 - Phase 4へ進むか、もう一度リトライ可能")
    else:
        print("⚠️ 成功率90%未満 - もう一度リトライを推奨")
        if still_failed:
            print("\nリトライコマンド:")
            print("python retry_specific.py --all")
    
    print("=" * 70)
    
    conn.close()

if __name__ == "__main__":
    check_retry_results()
