#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""データベースの現在の状況を確認（成功率表示版）"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/keiba.db')
cursor = conn.cursor()

print("=" * 70)
print("競馬予想家分析AI - 現在の進捗状況")
print("=" * 70)
print(f"確認日時: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
print()

# 予想家の処理状況
cursor.execute("SELECT COUNT(*) FROM predictors WHERE total_predictions > 0")
processed = cursor.fetchone()[0]
print(f"処理済み予想家: {processed}/186人 ({processed/186*100:.1f}%)")
print()

# 予想データの統計
cursor.execute("SELECT COUNT(*) FROM predictions")
total_predictions = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) 
    FROM predictions p 
    JOIN races r ON p.race_id = r.id
    WHERE r.grade IS NOT NULL
""")
grade_predictions = cursor.fetchone()[0]

print(f"総予想数: {total_predictions:,}件")
print(f"重賞予想数: {grade_predictions:,}件")
print()

# race_idの状況確認
cursor.execute("SELECT COUNT(*) FROM races WHERE race_id LIKE 'temp_%'")
temp_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM races WHERE race_id NOT LIKE 'temp_%'")
real_count = cursor.fetchone()[0]

print(f"temp形式のrace_id: {temp_count:,}件")
print(f"正しいrace_id: {real_count:,}件")
print()

# 成功率の計算（開始時点のtemp形式を8,995件と仮定）
initial_temp = 8995  # 開始時点のtemp件数
processed_count = initial_temp - temp_count
if processed_count > 0:
    success_count = real_count - 167  # 開始時点で167件あったので差分を計算
    # 統合完了分も含めた実際の処理件数
    actual_processed = initial_temp - temp_count
    success_rate = (success_count / actual_processed) * 100 if actual_processed > 0 else 0
    
    print("=" * 70)
    print("race_id更新の進捗")
    print("=" * 70)
    print(f"開始時点: {initial_temp:,}件")
    print(f"処理済み: {processed_count:,}件")
    print(f"残り: {temp_count:,}件")
    print(f"進捗率: {(processed_count/initial_temp)*100:.1f}%")
    print()
    print(f"成功（新規追加）: {success_count:,}件")
    print(f"成功（統合完了）: {processed_count - success_count:,}件")
    print(f"全体の完了率: {success_rate:.1f}%")
    print("=" * 70)
    print()

# レース詳細情報の状況
cursor.execute("SELECT COUNT(*) FROM races WHERE distance IS NOT NULL AND distance > 0")
detail_count = cursor.fetchone()[0]

print(f"詳細情報あり: {detail_count:,}件")
print(f"詳細情報なし: {temp_count + real_count - detail_count:,}件")
print()

# prediction_idの状況
cursor.execute("SELECT COUNT(*) FROM predictions WHERE netkeiba_prediction_id IS NOT NULL")
has_pred_id = cursor.fetchone()[0]

print(f"prediction_idあり: {has_pred_id:,}件")
print()

print("=" * 70)
print("次のステップ")
print("=" * 70)
if temp_count > 0:
    print(f"1. race_id更新: {temp_count:,}件のtemp形式を正しいIDに更新")
    print(f"   -> prediction_idから正しいrace_idを取得")
if temp_count + real_count - detail_count > 0:
    print(f"2. レース詳細取得: {temp_count + real_count - detail_count:,}件")
    print(f"   -> race_detail_scraper.pyを使用")
print("=" * 70)

conn.close()
