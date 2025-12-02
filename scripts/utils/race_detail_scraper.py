"""
レース詳細情報スクレイパー（バッチ処理最適化版）
race.netkeiba.com/race/result.html から詳細情報を取得してDBに保存
"""
import os
import sys
import time
import re
import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class RaceDetailScraper:
    """レース詳細情報を取得してDBに保存するスクレイパー"""
    
    def __init__(self, db_path: str = "keiba.db"):
        """初期化"""
        self.driver = None
        self.wait = None
        self.db_path = db_path
        
    def setup_driver(self):
        """Seleniumドライバーのセットアップ"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)
        logger.info("WebDriver setup completed")
        
    def close_driver(self):
        """ドライバーを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            
    def scrape_and_update(self, race_id: str, max_retries: int = 3) -> bool:
        """
        レース詳細を取得してDBを更新
        
        Args:
            race_id: レースID (例: 202505050211)
            max_retries: 最大リトライ回数
            
        Returns:
            成功時True、失敗時False
        """
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Scraping race_id={race_id} (attempt {attempt}/{max_retries})")
                
                # スクレイピング実行
                race_info = self._scrape_race_details(race_id)
                
                if not race_info:
                    logger.warning(f"No data retrieved for race_id={race_id}")
                    if attempt < max_retries:
                        logger.info(f"Retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                    return False
                
                # DB更新
                success = self._update_database(race_id, race_info)
                
                if success:
                    logger.info(f"✅ Successfully updated race_id={race_id}")
                    return True
                else:
                    logger.warning(f"Failed to update database for race_id={race_id}")
                    if attempt < max_retries:
                        logger.info(f"Retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                    return False
                    
            except Exception as e:
                logger.error(f"Error in attempt {attempt} for race_id={race_id}: {e}")
                if attempt < max_retries:
                    logger.info(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                return False
        
        return False
            
    def _scrape_race_details(self, race_id: str) -> Optional[Dict]:
        """
        レース詳細情報をスクレイピング
        
        Args:
            race_id: レースID
            
        Returns:
            レース詳細情報の辞書、エラー時はNone
        """
        url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}"
        
        try:
            if not self.driver:
                self.setup_driver()
                
            self.driver.get(url)
            time.sleep(2)  # ページ読み込み待機
            
            # レース情報を取得
            race_info = self._extract_race_info()
            
            if not race_info:
                logger.warning(f"Failed to extract race info for {race_id}")
                return None
            
            logger.debug(f"Extracted race info: {race_info}")
            return race_info
            
        except Exception as e:
            logger.error(f"Error scraping race {race_id}: {e}")
            return None
            
    def _extract_race_info(self) -> Dict:
        """レース基本情報を抽出（DB保存用の最小限の情報）"""
        info = {}
        
        try:
            # レース名
            race_name_elem = self.driver.find_element(By.CLASS_NAME, "RaceName")
            info['race_name'] = race_name_elem.text.strip().split('\n')[0]
            
            # レース条件（RaceData01）から距離・トラック取得
            race_data01 = self.driver.find_element(By.CLASS_NAME, "RaceData01").text
            
            # 距離・トラック
            distance_match = re.search(r'(芝|ダート)(\d+)m', race_data01)
            if distance_match:
                info['track_type'] = distance_match.group(1)
                info['distance'] = int(distance_match.group(2))
            else:
                info['track_type'] = '不明'
                info['distance'] = 0
                
            # 馬場状態
            track_condition_match = re.search(r'馬場:([^\s]+)', race_data01)
            info['track_condition'] = track_condition_match.group(1) if track_condition_match else None
            
            # レース詳細（RaceData02）から会場取得
            race_data02 = self.driver.find_element(By.CLASS_NAME, "RaceData02").text
            
            # 開催情報（例：5回東京2日目）
            kaisai_match = re.search(r'(\d+)回\s*(\S+)\s*(\d+)日目', race_data02)
            if kaisai_match:
                info['venue'] = kaisai_match.group(2)
            else:
                info['venue'] = '不明'
            
            # 頭数
            horses_match = re.search(r'(\d+)頭', race_data02)
            info['horse_count'] = int(horses_match.group(1)) if horses_match else 0
            
            logger.debug(f"Extracted: venue={info.get('venue')}, track_type={info.get('track_type')}, distance={info.get('distance')}")
            
        except Exception as e:
            logger.error(f"Error extracting race info: {e}")
            return {}
            
        return info
    
    def _update_database(self, race_id: str, race_info: Dict) -> bool:
        """
        データベースを更新
        
        Args:
            race_id: レースID
            race_info: レース情報
            
        Returns:
            成功時True、失敗時False
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # race_idでレコードを検索
            cursor.execute("SELECT id FROM races WHERE race_id = ?", (race_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Race not found in database: race_id={race_id}")
                conn.close()
                return False
            
            # 更新
            cursor.execute("""
                UPDATE races
                SET 
                    venue = ?,
                    distance = ?,
                    track_type = ?,
                    track_condition = ?,
                    horse_count = ?
                WHERE race_id = ?
            """, (
                race_info.get('venue', '不明'),
                race_info.get('distance', 0),
                race_info.get('track_type', '不明'),
                race_info.get('track_condition'),
                race_info.get('horse_count', 0),
                race_id
            ))
            
            conn.commit()
            
            # 更新確認
            if cursor.rowcount > 0:
                logger.info(f"Updated race_id={race_id}: venue={race_info.get('venue')}, track={race_info.get('track_type')}, distance={race_info.get('distance')}m")
                conn.close()
                return True
            else:
                logger.warning(f"No rows updated for race_id={race_id}")
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"Database update error for race_id={race_id}: {e}")
            if conn:
                conn.close()
            return False


def scrape_race_detail(race_id: str, db_path: str = "keiba.db") -> bool:
    """
    単一のレース詳細を取得してDBを更新（バッチ処理用のヘルパー関数）
    
    Args:
        race_id: レースID
        db_path: データベースパス
        
    Returns:
        成功時True、失敗時False
    """
    scraper = RaceDetailScraper(db_path)
    
    try:
        success = scraper.scrape_and_update(race_id)
        return success
    finally:
        scraper.close_driver()


def test_scraper():
    """スクレイパーのテスト"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting race detail scraper test...")
    
    scraper = RaceDetailScraper("keiba.db")
    
    try:
        # テスト用レースID（エリザベス女王杯G1）
        test_race_id = "202508040411"
        
        logger.info(f"Testing with race_id: {test_race_id}")
        
        success = scraper.scrape_and_update(test_race_id)
        
        if success:
            logger.info("✅ Test successful!")
            
            # DB確認
            conn = sqlite3.connect("keiba.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT race_id, race_name, venue, track_type, distance, horse_count
                FROM races
                WHERE race_id = ?
            """, (test_race_id,))
            row = cursor.fetchone()
            
            if row:
                logger.info(f"DB Record: {row}")
            
            conn.close()
        else:
            logger.error("❌ Test failed")
            
    except Exception as e:
        logger.exception(f"Test failed: {e}")
        
    finally:
        scraper.close_driver()


if __name__ == "__main__":
    test_scraper()
