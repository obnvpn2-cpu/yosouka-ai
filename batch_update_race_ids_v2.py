#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
race_id一括更新スクリプト（バッチ処理版 - UNIQUE制約エラー修正版）
全てのtemp形式race_idを自動的に更新

修正点：
- 既に更新済みのrace_idはスキップ
- UNIQUE制約違反を適切に処理
"""
import os
import sys
import time
import re
import sqlite3
from typing import Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from loguru import logger


class BatchRaceIDUpdater:
    """race_idを一括更新するクラス（修正版）"""
    
    def __init__(self, db_path='data/keiba.db', chromedriver_path=None):
        self.db_path = db_path
        self.driver = None
        self.chromedriver_path = chromedriver_path
        self.retry_limit = 3  # エラー時のリトライ回数
        
    def _cleanup_chrome_processes(self):
        """Chrome関連プロセスを完全にクリーンアップ"""
        try:
            os.system("taskkill /F /IM chromedriver.exe /T >nul 2>&1")
            time.sleep(1)
            os.system("taskkill /F /IM chrome.exe /T >nul 2>&1")
            time.sleep(1)
            logger.debug("Chrome processes cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up Chrome processes: {e}")
        
    def setup_driver(self):
        """Seleniumドライバーのセットアップ"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--proxy-server="direct://"')
            options.add_argument('--proxy-bypass-list=*')
            options.add_argument('--start-maximized')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--remote-debugging-port=0')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if self.chromedriver_path:
                driver_path = self.chromedriver_path
            else:
                project_root = os.path.dirname(os.path.abspath(__file__))
                driver_path = os.path.join(project_root, 'drivers', 'chromedriver.exe')
                
                if not os.path.exists(driver_path):
                    import shutil
                    system_driver = shutil.which('chromedriver')
                    if system_driver:
                        driver_path = system_driver
                    else:
                        raise FileNotFoundError("ChromeDriverが見つかりません。")
            
            logger.debug(f"Using ChromeDriver at: {driver_path}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            
            logger.debug("ChromeDriver setup completed!")
            
        except Exception as e:
            logger.error(f"Failed to setup ChromeDriver: {e}")
            raise
            
    def _safe_quit_driver(self):
        """ドライバーを安全に終了"""
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("Driver quit called")
            except Exception as e:
                logger.warning(f"Error during driver.quit(): {e}")
            finally:
                self.driver = None
            
            time.sleep(2)
            self._cleanup_chrome_processes()
            time.sleep(2)
            logger.debug("Driver safely closed")
            
    def get_race_id_from_prediction(self, prediction_id: int, retry_count: int = 0) -> Optional[str]:
        """
        prediction_idから正しいrace_idを取得（リトライ機能付き）
        
        Args:
            prediction_id: 予想ID
            retry_count: 現在のリトライ回数
            
        Returns:
            race_id (12桁) または None
        """
        url = f"https://yoso.netkeiba.com/?pid=yoso_detail&id={prediction_id}"
        
        try:
            # 既存のドライバーを完全に終了
            self._safe_quit_driver()
            
            # 新しいドライバーを初期化
            self.setup_driver()
            
            logger.debug(f"Loading page: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # race_idを含むリンクを探す
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and "race_id=" in href:
                        match = re.search(r'race_id=(\d{12})', href)
                        if match:
                            race_id = match.group(1)
                            logger.debug(f"Found race_id: {race_id}")
                            return race_id
                except Exception:
                    continue
                        
            logger.warning(f"No race_id found for prediction_id: {prediction_id}")
            return None
            
        except WebDriverException as e:
            logger.error(f"WebDriver error for prediction_id {prediction_id}: {e}")
            
            # リトライ
            if retry_count < self.retry_limit:
                logger.info(f"Retrying ({retry_count + 1}/{self.retry_limit})...")
                time.sleep(5)  # エラー時は長めに待機
                return self.get_race_id_from_prediction(prediction_id, retry_count + 1)
            else:
                logger.error(f"Failed after {self.retry_limit} retries")
                return None
                
        except Exception as e:
            logger.error(f"Error getting race_id for prediction_id {prediction_id}: {e}")
            
            # リトライ
            if retry_count < self.retry_limit:
                logger.info(f"Retrying ({retry_count + 1}/{self.retry_limit})...")
                time.sleep(5)
                return self.get_race_id_from_prediction(prediction_id, retry_count + 1)
            else:
                return None
                
        finally:
            self._safe_quit_driver()
            
    def batch_update_all(self, batch_size: int = 100):
        """
        全てのrace_idを一括更新
        
        Args:
            batch_size: 1バッチあたりの処理件数
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 全体の件数を確認（temp形式のrace_idのみ）
            cursor.execute("""
                SELECT COUNT(DISTINCT r.id)
                FROM races r
                WHERE r.race_id LIKE 'temp_%'
            """)
            total_count = cursor.fetchone()[0]
            
            logger.info("=" * 70)
            logger.info(f"全体: {total_count}件のrace_idを更新します")
            logger.info(f"バッチサイズ: {batch_size}件")
            logger.info(f"推定バッチ数: {(total_count + batch_size - 1) // batch_size}回")
            logger.info("=" * 70)
            logger.info("")
            
            batch_num = 1
            total_success = 0
            total_fail = 0
            total_skip = 0
            failed_predictions = []
            
            start_time = time.time()
            
            while True:
                batch_start_time = time.time()
                
                # バッチ処理（常にoffset=0で取得、処理済みは自動的に除外される）
                success, fail, skip, failed_ids = self._process_batch(batch_size)
                
                if success == 0 and fail == 0 and skip == 0:
                    # 処理するものがなくなった
                    logger.info("処理対象のrace_idがなくなりました")
                    break
                
                total_success += success
                total_fail += fail
                total_skip += skip
                failed_predictions.extend(failed_ids)
                
                # 現在の進捗を確認
                cursor.execute("SELECT COUNT(*) FROM races WHERE race_id LIKE 'temp_%'")
                remaining = cursor.fetchone()[0]
                
                # バッチの処理時間
                batch_elapsed = time.time() - batch_start_time
                
                logger.info("=" * 70)
                logger.info(f"バッチ {batch_num} 完了: 成功={success}, 失敗={fail}, スキップ={skip}, 処理時間={batch_elapsed:.1f}秒")
                logger.info(f"残り: {remaining}件 / 元: {total_count}件")
                
                # 進捗状況
                progress = ((total_count - remaining) / total_count) * 100
                elapsed_total = time.time() - start_time
                if total_success > 0:
                    avg_time_per_item = elapsed_total / total_success
                    eta_seconds = remaining * avg_time_per_item
                    eta_hours = eta_seconds / 3600
                    logger.info(f"進捗: {progress:.1f}% | 累計成功: {total_success} | 累計失敗: {total_fail} | 推定残り時間: {eta_hours:.1f}時間")
                logger.info("=" * 70)
                logger.info("")
                
                batch_num += 1
                
                # 終了条件
                if remaining == 0:
                    logger.success("全てのrace_idが更新されました！")
                    break
                
                # バッチ間で休憩（サーバー負荷軽減）
                logger.info("次のバッチまで10秒待機...")
                time.sleep(10)
                
            # 最終結果
            total_elapsed = time.time() - start_time
            logger.info("=" * 70)
            logger.success("全バッチ処理完了！")
            logger.info("=" * 70)
            logger.success(f"成功: {total_success}")
            if total_fail > 0:
                logger.error(f"失敗: {total_fail}")
                logger.error(f"失敗したprediction_id: {failed_predictions[:10]}..." if len(failed_predictions) > 10 else f"失敗したprediction_id: {failed_predictions}")
            if total_skip > 0:
                logger.info(f"スキップ: {total_skip}")
            logger.info(f"総処理時間: {total_elapsed / 3600:.1f}時間")
            logger.info("=" * 70)
            
        except KeyboardInterrupt:
            logger.warning("処理が中断されました")
            logger.info(f"現在までの成功: {total_success}, 失敗: {total_fail}, スキップ: {total_skip}")
        except Exception as e:
            logger.exception(f"バッチ処理中にエラー: {e}")
            conn.rollback()
        finally:
            conn.close()
            self._safe_quit_driver()
            self._cleanup_chrome_processes()
            
    def _process_batch(self, limit: int):
        """1バッチ分の処理（修正版 - UNIQUE制約対応）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # temp形式のrace_idを持つレースを取得（常にoffset=0）
            # 処理済みのものは自動的に除外される
            cursor.execute("""
                SELECT r.id, r.race_id
                FROM races r
                WHERE r.race_id LIKE 'temp_%'
                LIMIT ?
            """, (limit,))
            
            races_to_update = cursor.fetchall()
            total = len(races_to_update)
            
            if total == 0:
                return 0, 0, 0, []
            
            logger.info("=" * 70)
            logger.info(f"バッチ処理開始: {total}件")
            logger.info("=" * 70)
            
            success_count = 0
            fail_count = 0
            skip_count = 0
            failed_ids = []
            
            for i, (race_internal_id, temp_race_id) in enumerate(races_to_update, 1):
                # このレースに関連するprediction_idを1つ取得
                cursor.execute("""
                    SELECT netkeiba_prediction_id
                    FROM predictions
                    WHERE race_id = ?
                    AND netkeiba_prediction_id IS NOT NULL
                    LIMIT 1
                """, (race_internal_id,))
                
                result = cursor.fetchone()
                if not result:
                    logger.warning(f"  [{i}/{total}] prediction_idが見つかりません: race_id={temp_race_id}")
                    skip_count += 1
                    continue
                
                prediction_id = result[0]
                logger.info(f"  [{i}/{total}] race_internal_id={race_internal_id}, prediction_id={prediction_id}")
                
                # 念のため、まだtemp形式か再確認
                cursor.execute("SELECT race_id FROM races WHERE id = ?", (race_internal_id,))
                current_race_id = cursor.fetchone()[0]
                
                if not current_race_id.startswith('temp_'):
                    logger.info(f"  ⏭️  既に更新済み: {current_race_id}")
                    skip_count += 1
                    continue
                
                # 正しいrace_idを取得
                real_race_id = self.get_race_id_from_prediction(prediction_id)
                
                if real_race_id:
                    try:
                        # race_idを更新
                        cursor.execute("""
                            UPDATE races
                            SET race_id = ?
                            WHERE id = ?
                        """, (real_race_id, race_internal_id))
                        
                        conn.commit()
                        logger.success(f"  ✅ {current_race_id} -> {real_race_id}")
                        success_count += 1
                        
                    except sqlite3.IntegrityError as e:
                        # UNIQUE制約違反 - 既に同じrace_idが存在する
                        logger.warning(f"  ⚠️  重複: {real_race_id} は既に存在")
                        
                        # このtemp_race_idのレコードを削除し、既存のrace_idに統合
                        # まず、既存のrace_idのIDを取得
                        cursor.execute("SELECT id FROM races WHERE race_id = ?", (real_race_id,))
                        existing_result = cursor.fetchone()
                        
                        if existing_result:
                            existing_race_id = existing_result[0]
                            
                            # predictionsの参照を既存のrace_idに変更
                            cursor.execute("""
                                UPDATE predictions
                                SET race_id = ?
                                WHERE race_id = ?
                            """, (existing_race_id, race_internal_id))
                            
                            # 古いtemp_race_idのレコードを削除
                            cursor.execute("DELETE FROM races WHERE id = ?", (race_internal_id,))
                            
                            conn.commit()
                            logger.success(f"  ✅ 統合完了: {current_race_id} -> {real_race_id} (既存レコードに統合)")
                            success_count += 1
                        else:
                            logger.error(f"  ❌ 既存レコードが見つかりません: {real_race_id}")
                            fail_count += 1
                            
                else:
                    logger.error(f"  ❌ Failed: prediction_id={prediction_id}")
                    fail_count += 1
                    failed_ids.append(prediction_id)
                    
                # 負荷軽減のため待機
                time.sleep(2)
                
            return success_count, fail_count, skip_count, failed_ids
            
        except Exception as e:
            logger.exception(f"バッチ処理中にエラー: {e}")
            conn.rollback()
            return 0, 0, 0, []
        finally:
            conn.close()


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description='race_id一括更新スクリプト（修正版）')
    parser.add_argument('--batch-size', type=int, default=100, help='1バッチあたりの処理件数（デフォルト: 100）')
    parser.add_argument('--db', type=str, default='data/keiba.db', help='データベースパス')
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("race_id一括更新スクリプト開始（修正版 - UNIQUE制約対応）")
    logger.info("=" * 70)
    logger.info(f"開始時刻: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
    logger.info("")
    
    updater = BatchRaceIDUpdater(db_path=args.db)
    
    try:
        updater.batch_update_all(batch_size=args.batch_size)
        
        logger.info("")
        logger.info(f"終了時刻: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
        logger.success("=" * 70)
        logger.success("全処理が完了しました！")
        logger.success("=" * 70)
        logger.info("")
        logger.info("次のステップ: レース詳細情報の取得")
        logger.info("コマンド: python check_db_status.py")
        
    except KeyboardInterrupt:
        logger.warning("\n処理が中断されました")
        logger.info("再開する場合は同じコマンドを実行してください")
    except Exception as e:
        logger.exception(f"エラーが発生しました: {e}")
    finally:
        updater._safe_quit_driver()
        updater._cleanup_chrome_processes()


if __name__ == "__main__":
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # ログファイルにも出力
    log_filename = f"logs/batch_update_race_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger.add(log_filename, rotation="100 MB", retention="7 days")
    logger.info(f"ログファイル: {log_filename}")
    
    main()
