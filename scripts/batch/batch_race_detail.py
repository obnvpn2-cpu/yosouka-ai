#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
レース詳細情報のバッチ取得スクリプト（pandas版スクレイパー対応 + 100件ごと30分休憩）
"""

import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sqlite3

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ログ設定
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"batch_race_detail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RaceDetailBatchProcessor:
    """レース詳細情報のバッチ処理クラス（100件ごと30分休憩機能付き）"""
    
    def __init__(self, db_path: str = "data/keiba.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect_db(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"データベース接続成功: {self.db_path}")
        except Exception as e:
            logger.error(f"データベース接続エラー: {e}")
            raise
    
    def close_db(self):
        """データベース切断"""
        if self.conn:
            self.conn.close()
            logger.info("データベース切断")
    
    def get_pending_races(
        self, 
        offset: int = 0, 
        limit: Optional[int] = None,
        grade_only: bool = False
    ) -> List[Dict]:
        """詳細未取得のレース一覧を取得"""
        query = """
            SELECT id, race_id, race_name, grade, is_grade_race
            FROM races
            WHERE track_type = '不明' OR track_type IS NULL
        """
        
        if grade_only:
            query += " AND is_grade_race = 1"
        
        query += " ORDER BY id"
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        self.cursor.execute(query)
        races = []
        for row in self.cursor.fetchall():
            races.append({
                'id': row[0],
                'race_id': row[1],
                'race_name': row[2],
                'grade': row[3],
                'is_grade_race': row[4]
            })
        
        return races
    
    def get_stats(self) -> Dict:
        """統計情報を取得"""
        stats = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM races")
        stats['total_races'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM races WHERE track_type IS NOT NULL AND track_type != '不明'")
        stats['completed'] = self.cursor.fetchone()[0]
        
        stats['pending'] = stats['total_races'] - stats['completed']
        
        self.cursor.execute("SELECT COUNT(*) FROM races WHERE is_grade_race = 1")
        stats['grade_races'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("""
            SELECT COUNT(*) FROM races 
            WHERE is_grade_race = 1 AND (track_type IS NULL OR track_type = '不明')
        """)
        stats['grade_pending'] = self.cursor.fetchone()[0]
        
        return stats
    
    def _sleep_with_countdown(self, seconds: int, message: str):
        """カウントダウン付き休憩"""
        logger.info(f"💤 {message}")
        logger.info(f"   休憩時間: {seconds}秒（{seconds/60:.0f}分）")
        
        remaining = seconds
        start_time = time.time()
        
        while remaining > 0:
            mins = remaining // 60
            secs = remaining % 60
            
            if remaining == seconds or remaining % 60 == 0:  # 開始時と1分ごと
                eta = datetime.now() + timedelta(seconds=remaining)
                logger.info(f"   ⏰ 残り: {mins}分{secs}秒 | 再開予定: {eta.strftime('%H:%M:%S')}")
            
            time.sleep(min(60, remaining))  # 最大1分待機
            elapsed = int(time.time() - start_time)
            remaining = seconds - elapsed
        
        logger.info(f"   ✅ 休憩終了。処理を再開します。")
    
    def process_batch(
        self,
        offset: int = 0,
        limit: Optional[int] = None,
        grade_only: bool = False,
        sleep_interval: int = 3,
        batch_interval: int = 1800  # 100件ごとの休憩時間（秒）デフォルト30分
    ):
        """バッチ処理を実行"""
        self.connect_db()
        
        try:
            # 統計表示
            stats = self.get_stats()
            logger.info("=" * 60)
            logger.info("レース詳細バッチ処理開始（pandas版 + 100件ごと休憩）")
            logger.info("=" * 60)
            logger.info(f"総レース数: {stats['total_races']}件")
            logger.info(f"詳細取得済み: {stats['completed']}件 ({stats['completed']/stats['total_races']*100:.1f}%)")
            logger.info(f"詳細未取得: {stats['pending']}件")
            logger.info(f"重賞: {stats['grade_races']}件（未取得: {stats['grade_pending']}件）")
            logger.info("=" * 60)
            
            # 処理対象レース取得
            races = self.get_pending_races(offset, limit, grade_only)
            
            if not races:
                logger.info("処理対象のレースがありません")
                return
            
            logger.info(f"処理対象: {len(races)}件")
            if grade_only:
                logger.info("（重賞のみ）")
            logger.info(f"範囲: offset={offset}, limit={limit}")
            
            # 推定時刻を計算
            num_batches = (len(races) - 1) // 100  # 休憩回数
            estimated_process_time = len(races) * 6  # 秒（平均6秒/件）
            estimated_wait_time = len(races) * sleep_interval  # レース間待機
            estimated_interval_time = num_batches * batch_interval  # 100件ごと休憩
            total_estimated_time = estimated_process_time + estimated_wait_time + estimated_interval_time
            estimated_completion = datetime.now() + timedelta(seconds=total_estimated_time)
            
            logger.info(f"")
            logger.info(f"⏱️  推定所要時間: {total_estimated_time/3600:.1f}時間")
            logger.info(f"   - 処理時間: {estimated_process_time/60:.0f}分")
            logger.info(f"   - レース間待機: {estimated_wait_time/60:.0f}分")
            logger.info(f"   - 100件ごと休憩: {num_batches}回 × {batch_interval/60:.0f}分 = {estimated_interval_time/60:.0f}分")
            logger.info(f"🎯 推定完了時刻: {estimated_completion.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # race_detail_scraperをインポート
            try:
                from backend.scraper.race_detail_scraper_with_db import scrape_race_detail
            except ImportError:
                logger.error("race_detail_scraper_with_db.pyが見つかりません")
                logger.error("backend/scraper/race_detail_scraper_with_db.pyが存在することを確認してください")
                return
            
            # 処理開始
            success_count = 0
            error_count = 0
            start_time = time.time()
            
            for i, race in enumerate(races, 1):
                try:
                    logger.info(f"\n[{i}/{len(races)}] 処理中: {race['race_name']} (race_id: {race['race_id']})")
                    if race['is_grade_race']:
                        logger.info(f"  グレード: {race['grade']}")
                    
                    # レース詳細取得
                    success = scrape_race_detail(race['race_id'], self.db_path)
                    
                    if success:
                        success_count += 1
                        logger.info(f"  ✅ 成功 ({success_count}/{len(races)})")
                    else:
                        error_count += 1
                        logger.warning(f"  ❌ 失敗 ({error_count}/{len(races)})")
                    
                    # 進捗表示
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining_races = len(races) - i
                    remaining_batches = remaining_races // 100
                    remaining_process_time = remaining_races * avg_time
                    remaining_interval_time = remaining_batches * batch_interval
                    total_remaining = remaining_process_time + remaining_interval_time
                    
                    eta = datetime.now() + timedelta(seconds=total_remaining)
                    logger.info(f"  進捗: {i/len(races)*100:.1f}% | 経過: {elapsed/60:.1f}分 | 残り: {total_remaining/60:.1f}分 | ETA: {eta.strftime('%H:%M:%S')}")
                    
                    # 100件ごとに30分休憩（最後のレースでない場合）
                    if i % 100 == 0 and i < len(races):
                        logger.info("")
                        logger.info("🎉" + "=" * 58)
                        logger.info(f"🎉 100件処理完了！ ({i}/{len(races)}件)")
                        logger.info("🎉" + "=" * 58)
                        self._sleep_with_countdown(
                            batch_interval,
                            f"netkeiba.comへの負荷軽減のため{batch_interval/60:.0f}分休憩します..."
                        )
                        logger.info("")
                        logger.info("🚀" + "=" * 58)
                        logger.info(f"🚀 処理再開: 残り{len(races)-i}件")
                        logger.info("🚀" + "=" * 58)
                    
                    # レース間待機（最後のレース以外、かつ100件目でない場合）
                    elif i < len(races):
                        logger.info(f"  待機: {sleep_interval}秒...")
                        time.sleep(sleep_interval)
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"  エラー: {race['race_name']} - {e}")
                    continue
            
            # 結果サマリー
            total_time = time.time() - start_time
            logger.info("\n" + "=" * 60)
            logger.info("🎊 バッチ処理完了")
            logger.info("=" * 60)
            logger.info(f"処理件数: {len(races)}件")
            logger.info(f"成功: {success_count}件 ({success_count/len(races)*100:.1f}%)")
            logger.info(f"失敗: {error_count}件 ({error_count/len(races)*100:.1f}%)")
            logger.info(f"処理時間: {total_time/3600:.1f}時間 ({total_time/60:.1f}分)")
            logger.info(f"平均処理時間: {total_time/len(races):.1f}秒/件")
            logger.info("=" * 60)
            
            # 最新統計
            stats = self.get_stats()
            logger.info(f"\n現在の状況:")
            logger.info(f"詳細取得済み: {stats['completed']}/{stats['total_races']}件 ({stats['completed']/stats['total_races']*100:.1f}%)")
            logger.info(f"詳細未取得: {stats['pending']}件")
            
        finally:
            self.close_db()


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='レース詳細情報のバッチ取得（pandas版 + 100件ごと休憩）')
    
    parser.add_argument('--offset', type=int, default=0, help='開始位置（デフォルト: 0）')
    parser.add_argument('--limit', type=int, default=None, help='取得件数（デフォルト: 全件）')
    parser.add_argument('--grade-only', action='store_true', help='重賞のみ取得')
    parser.add_argument('--sleep', type=int, default=3, help='各レース処理後の待機秒数（デフォルト: 3）')
    parser.add_argument('--batch-interval', type=int, default=1800, help='100件ごとの休憩時間（秒）（デフォルト: 1800秒=30分）')
    parser.add_argument('--db', type=str, default='data/keiba.db', help='データベースパス')
    
    args = parser.parse_args()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("⚙️  設定:")
    logger.info(f"   レース間待機: {args.sleep}秒")
    logger.info(f"   100件ごと休憩: {args.batch_interval}秒 ({args.batch_interval/60:.0f}分)")
    logger.info("=" * 60)
    logger.info("")
    
    # バッチ処理実行
    processor = RaceDetailBatchProcessor(args.db)
    processor.process_batch(
        offset=args.offset,
        limit=args.limit,
        grade_only=args.grade_only,
        sleep_interval=args.sleep,
        batch_interval=args.batch_interval
    )


if __name__ == "__main__":
    main()
