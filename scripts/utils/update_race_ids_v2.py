#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
race_id更新スクリプト（改善版 - prediction.pyのベストプラクティス適用）
temp形式のrace_idを正しいrace_idに更新

処理フロー:
1. prediction_idを持つ予想データを取得
2. 予想詳細ページにアクセスしてrace_idを抽出
3. racesテーブルのrace_idを更新
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


class RaceIDUpdater:
    """race_idを更新するクラス（prediction.pyのベストプラクティス適用）"""
    
    def __init__(self, db_path='data/keiba.db', chromedriver_path=None):
        self.db_path = db_path
        self.driver = None
        self.chromedriver_path = chromedriver_path
        
    def _cleanup_chrome_processes(self):
        """Chrome関連プロセスを完全にクリーンアップ（prediction.pyより）"""
        try:
            # ChromeDriverを終了
            os.system("taskkill /F /IM chromedriver.exe /T >nul 2>&1")
            time.sleep(1)
            # Chrome本体も終了
            os.system("taskkill /F /IM chrome.exe /T >nul 2>&1")
            time.sleep(1)
            logger.debug("Chrome processes cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up Chrome processes: {e}")
        
    def setup_driver(self):
        """Seleniumドライバーのセットアップ（prediction.pyのオプションを適用）"""
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
        """ドライバーを安全に終了（prediction.pyより）"""
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
            
    def get_race_id_from_prediction(self, prediction_id: int) -> Optional[str]:
        """
        prediction_idから正しいrace_idを取得
        各リクエストごとにドライバーを起動・終了（prediction.pyのアプローチ）
        
        Args:
            prediction_id: 予想ID
            
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
            time.sleep(3)  # ページ読み込み待機
            
            # race_idを含むリンクを探す
            # <a href="?pid=race_yoso_list&race_id=202508040411">
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and "race_id=" in href:
                        # race_idを抽出
                        match = re.search(r'race_id=(\d{12})', href)
                        if match:
                            race_id = match.group(1)
                            logger.debug(f"Found race_id: {race_id}")
                            return race_id
                except Exception as e:
                    # 個別のリンク処理でのエラーは無視
                    continue
                        
            logger.warning(f"No race_id found for prediction_id: {prediction_id}")
            return None
            
        except WebDriverException as e:
            logger.error(f"WebDriver error for prediction_id {prediction_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting race_id for prediction_id {prediction_id}: {e}")
            return None
        finally:
            # 必ずドライバーを終了
            self._safe_quit_driver()
            
    def update_race_ids(self, limit: int = 10, offset: int = 0):
        """
        race_idを更新
        
        Args:
            limit: 処理件数
            offset: オフセット
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # temp形式のrace_idを持つレースを取得
            cursor.execute("""
                SELECT DISTINCT r.id, r.race_id, p.netkeiba_prediction_id
                FROM races r
                JOIN predictions p ON r.id = p.race_id
                WHERE r.race_id LIKE 'temp_%'
                AND p.netkeiba_prediction_id IS NOT NULL
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            races_to_update = cursor.fetchall()
            total = len(races_to_update)
            
            logger.info(f"Updating {total} race_ids (offset: {offset})")
            
            success_count = 0
            fail_count = 0
            
            for i, (race_internal_id, temp_race_id, prediction_id) in enumerate(races_to_update, 1):
                logger.info(f"[{i}/{total}] Processing: temp_race_id={temp_race_id}, prediction_id={prediction_id}")
                
                # 正しいrace_idを取得（各リクエストごとにドライバーを起動・終了）
                real_race_id = self.get_race_id_from_prediction(prediction_id)
                
                if real_race_id:
                    # race_idを更新
                    cursor.execute("""
                        UPDATE races
                        SET race_id = ?
                        WHERE id = ?
                    """, (real_race_id, race_internal_id))
                    
                    conn.commit()
                    logger.success(f"Updated: {temp_race_id} -> {real_race_id}")
                    success_count += 1
                else:
                    logger.error(f"Failed to get race_id for prediction_id: {prediction_id}")
                    fail_count += 1
                    
                # 負荷軽減のため待機（prediction.pyと同様）
                time.sleep(2)
                
            logger.info("=" * 70)
            logger.success(f"Success: {success_count}/{total}")
            if fail_count > 0:
                logger.error(f"Failed: {fail_count}/{total}")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.exception(f"Error updating race_ids: {e}")
            conn.rollback()
        finally:
            conn.close()
            
    def get_progress(self):
        """現在の進捗を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM races WHERE race_id LIKE 'temp_%'")
        temp_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM races WHERE race_id NOT LIKE 'temp_%'")
        real_count = cursor.fetchone()[0]
        
        conn.close()
        
        total = temp_count + real_count
        progress = (real_count / total * 100) if total > 0 else 0
        
        return {
            'temp_count': temp_count,
            'real_count': real_count,
            'total': total,
            'progress': progress
        }


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description='race_id更新スクリプト')
    parser.add_argument('--limit', type=int, default=10, help='処理件数（デフォルト: 10）')
    parser.add_argument('--offset', type=int, default=0, help='オフセット（デフォルト: 0）')
    parser.add_argument('--db', type=str, default='data/keiba.db', help='データベースパス')
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("race_id更新スクリプト開始（改善版）")
    logger.info("=" * 70)
    
    updater = RaceIDUpdater(db_path=args.db)
    
    try:
        # 開始前の進捗確認
        before = updater.get_progress()
        logger.info(f"開始前: temp={before['temp_count']}, real={before['real_count']}, 進捗={before['progress']:.1f}%")
        logger.info("")
        
        # race_id更新実行
        updater.update_race_ids(limit=args.limit, offset=args.offset)
        
        # 終了後の進捗確認
        after = updater.get_progress()
        logger.info("")
        logger.info(f"終了後: temp={after['temp_count']}, real={after['real_count']}, 進捗={after['progress']:.1f}%")
        logger.info("")
        
        # 次回のコマンド
        if after['temp_count'] > 0:
            next_offset = args.offset + args.limit
            logger.info("=" * 70)
            logger.info("次回実行コマンド:")
            logger.info(f"python update_race_ids.py --limit {args.limit} --offset {next_offset}")
            logger.info("=" * 70)
        else:
            logger.success("=" * 70)
            logger.success("全てのrace_id更新が完了しました！")
            logger.success("=" * 70)
            
    except KeyboardInterrupt:
        logger.warning("処理が中断されました")
    except Exception as e:
        logger.exception(f"エラーが発生しました: {e}")
    finally:
        # 最終クリーンアップ
        updater._safe_quit_driver()
        updater._cleanup_chrome_processes()


if __name__ == "__main__":
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    logger.add("logs/update_race_ids_{time}.log", rotation="1 day", retention="7 days")
    
    main()
