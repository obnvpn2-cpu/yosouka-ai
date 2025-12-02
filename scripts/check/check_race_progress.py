#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
レース詳細取得の進捗監視・管理スクリプト

使用方法:
    # 現在の進捗確認
    python check_race_progress.py
    
    # 詳細表示
    python check_race_progress.py --verbose
    
    # 重賞の進捗のみ
    python check_race_progress.py --grade-only
"""

import sys
import argparse
import sqlite3
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).resolve().parent
db_path = project_root / "keiba.db"


def get_progress_stats(db_path: str, verbose: bool = False) -> Dict:
    """進捗統計を取得"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # 総レース数
    cursor.execute("SELECT COUNT(*) FROM races")
    stats['total_races'] = cursor.fetchone()[0]
    
    # 詳細取得済み
    cursor.execute("SELECT COUNT(*) FROM races WHERE track_type != '不明' AND track_type IS NOT NULL")
    stats['completed'] = cursor.fetchone()[0]
    
    # 詳細未取得
    stats['pending'] = stats['total_races'] - stats['completed']
    
    # 進捗率
    if stats['total_races'] > 0:
        stats['progress_pct'] = stats['completed'] / stats['total_races'] * 100
    else:
        stats['progress_pct'] = 0
    
    # 重賞統計
    cursor.execute("SELECT COUNT(*) FROM races WHERE is_grade_race = 1")
    stats['grade_races'] = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM races 
        WHERE is_grade_race = 1 AND track_type != '不明' AND track_type IS NOT NULL
    """)
    stats['grade_completed'] = cursor.fetchone()[0]
    
    stats['grade_pending'] = stats['grade_races'] - stats['grade_completed']
    
    if stats['grade_races'] > 0:
        stats['grade_progress_pct'] = stats['grade_completed'] / stats['grade_races'] * 100
    else:
        stats['grade_progress_pct'] = 0
    
    # グレード別統計
    if verbose:
        stats['by_grade'] = {}
        for grade in ['G1', 'G2', 'G3']:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN track_type != '不明' AND track_type IS NOT NULL THEN 1 END) as completed
                FROM races
                WHERE grade = '{grade}'
            """)
            row = cursor.fetchone()
            stats['by_grade'][grade] = {
                'total': row[0],
                'completed': row[1],
                'pending': row[0] - row[1],
                'progress_pct': row[1] / row[0] * 100 if row[0] > 0 else 0
            }
    
    # コース別統計
    if verbose:
        cursor.execute("""
            SELECT track_type, COUNT(*) as count
            FROM races
            WHERE track_type IS NOT NULL AND track_type != '不明'
            GROUP BY track_type
            ORDER BY count DESC
        """)
        stats['by_course'] = {}
        for row in cursor.fetchall():
            if row[0]:
                stats['by_course'][row[0]] = row[1]
    
    # 場所別統計
    if verbose:
        cursor.execute("""
            SELECT venue, COUNT(*) as count
            FROM races
            WHERE venue IS NOT NULL AND venue != '不明'
            GROUP BY venue
            ORDER BY count DESC
        """)
        stats['by_track'] = {}
        for row in cursor.fetchall():
            if row[0]:
                stats['by_track'][row[0]] = row[1]
    
    conn.close()
    return stats


def display_progress(stats: Dict, verbose: bool = False):
    """進捗を表示"""
    print("\n" + "=" * 60)
    print("レース詳細取得 進捗レポート")
    print("=" * 60)
    
    # 全体進捗
    print(f"\n【全体】")
    print(f"総レース数: {stats['total_races']:,}件")
    print(f"詳細取得済み: {stats['completed']:,}件 ({stats['progress_pct']:.1f}%)")
    print(f"詳細未取得: {stats['pending']:,}件")
    
    # プログレスバー
    bar_length = 40
    filled = int(bar_length * stats['progress_pct'] / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\n進捗: [{bar}] {stats['progress_pct']:.1f}%")
    
    # 重賞進捗
    print(f"\n【重賞】")
    print(f"重賞レース数: {stats['grade_races']:,}件")
    print(f"詳細取得済み: {stats['grade_completed']:,}件 ({stats['grade_progress_pct']:.1f}%)")
    print(f"詳細未取得: {stats['grade_pending']:,}件")
    
    # 重賞プログレスバー
    filled = int(bar_length * stats['grade_progress_pct'] / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\n進捗: [{bar}] {stats['grade_progress_pct']:.1f}%")
    
    # 詳細情報
    if verbose and 'by_grade' in stats:
        print(f"\n【グレード別】")
        for grade in ['G1', 'G2', 'G3']:
            if grade in stats['by_grade']:
                g = stats['by_grade'][grade]
                print(f"{grade}: {g['completed']}/{g['total']}件 ({g['progress_pct']:.1f}%) - 残り{g['pending']}件")
    
    if verbose and 'by_course' in stats:
        print(f"\n【コース別】（取得済みのみ）")
        for course, count in sorted(stats['by_course'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"{course}: {count}件")
    
    if verbose and 'by_track' in stats:
        print(f"\n【競馬場別】（取得済みのみ）")
        for track, count in sorted(stats['by_track'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{track}: {count}件")
    
    print("\n" + "=" * 60)


def get_next_command(stats: Dict) -> str:
    """次に実行すべきコマンドを提案"""
    if stats['pending'] == 0:
        return "✅ 全レースの詳細取得が完了しました！"
    
    # 推奨バッチサイズ
    batch_size = min(100, stats['pending'])
    
    commands = []
    commands.append(f"\n【次に実行すべきコマンド】")
    commands.append(f"\n# 次の{batch_size}件を取得（推奨）")
    commands.append(f"python batch_race_detail.py --limit {batch_size}")
    
    if stats['grade_pending'] > 0:
        grade_batch = min(50, stats['grade_pending'])
        commands.append(f"\n# 重賞のみ{grade_batch}件取得")
        commands.append(f"python batch_race_detail.py --limit {grade_batch} --grade-only")
    
    commands.append(f"\n# 全件取得（残り{stats['pending']}件）")
    commands.append(f"python batch_race_detail.py")
    
    return "\n".join(commands)


def main():
    parser = argparse.ArgumentParser(description='レース詳細取得の進捗確認')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細表示')
    parser.add_argument('--grade-only', '-g', action='store_true', help='重賞のみ表示')
    parser.add_argument('--db', type=str, default='keiba.db', help='データベースパス')
    
    args = parser.parse_args()
    
    try:
        # 進捗取得
        stats = get_progress_stats(args.db, args.verbose)
        
        # 表示
        display_progress(stats, args.verbose)
        
        # 次のコマンド提案
        if not args.grade_only:
            print(get_next_command(stats))
        
    except FileNotFoundError:
        print(f"❌ エラー: データベースファイルが見つかりません: {args.db}")
        print("プロジェクトのルートディレクトリで実行してください。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
