"""
レース詳細情報スクレイパー（DB更新機能付き）
"""
import os
import sys
import time
import re
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from loguru import logger


class RaceDetailScraperWithDB:
    """レース詳細情報を取得してDBに保存するスクレイパー"""
    
    def __init__(self, db_path="data/keiba.db", chromedriver_path=None):
        """初期化"""
        self.driver = None
        self.wait = None
        self.db_path = db_path
        self.chromedriver_path = chromedriver_path
        
    def setup_driver(self):
        """Seleniumドライバーのセットアップ"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            if self.chromedriver_path:
                driver_path = self.chromedriver_path
            else:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
            self.wait = WebDriverWait(self.driver, 15)
            logger.debug("ChromeDriver setup completed!")
            
        except Exception as e:
            logger.error(f"Failed to setup ChromeDriver: {e}")
            raise
        
    def close_driver(self):
        """ドライバーを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
    
    def scrape_and_update(self, race_id: str, max_retries: int = 3) -> bool:
        """
        レース詳細を取得してDBを更新
        
        Args:
            race_id: レースID
            max_retries: 最大リトライ回数
            
        Returns:
            成功時True、失敗時False
        """
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Scraping race_id={race_id} (attempt {attempt}/{max_retries})")
                
                # スクレイピング実行
                race_data = self._scrape_race_details(race_id)
                
                if not race_data or not race_data.get('race_info'):
                    logger.warning(f"No data retrieved for race_id={race_id}")
                    if attempt < max_retries:
                        time.sleep(5)
                        continue
                    return False
                
                # DB更新
                success = self._update_database(race_id, race_data)
                
                if success:
                    logger.info(f"✅ Successfully updated race_id={race_id}")
                    return True
                else:
                    if attempt < max_retries:
                        time.sleep(5)
                        continue
                    return False
                    
            except Exception as e:
                logger.error(f"Error in attempt {attempt} for race_id={race_id}: {e}")
                if attempt < max_retries:
                    time.sleep(5)
                    continue
                return False
        
        return False
    
    def _scrape_race_details(self, race_id: str) -> Optional[Dict]:
        """レース詳細をスクレイピング"""
        url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}"
        
        try:
            if not self.driver:
                self.setup_driver()
                
            self.driver.get(url)
            time.sleep(2)
            
            race_info = self._extract_race_info()
            
            if not race_info:
                return None
            
            return {
                'race_id': race_id,
                'race_info': race_info,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping race {race_id}: {e}")
            return None
    
    def _extract_race_info(self) -> Dict:
        """レース基本情報を抽出"""
        info = {}
        
        try:
            race_name_elem = self.driver.find_element(By.CLASS_NAME, "RaceName")
            info['race_name'] = race_name_elem.text.strip().split('\n')[0]
            
            race_data01 = self.driver.find_element(By.CLASS_NAME, "RaceData01").text
            
            distance_match = re.search(r'(芝|ダート)(\d+)m', race_data01)
            if distance_match:
                info['track_type'] = distance_match.group(1)
                info['distance'] = int(distance_match.group(2))
            else:
                info['track_type'] = '不明'
                info['distance'] = 0
                
            track_condition_match = re.search(r'馬場:([^\s]+)', race_data01)
            info['track_condition'] = track_condition_match.group(1) if track_condition_match else None
            
            race_data02 = self.driver.find_element(By.CLASS_NAME, "RaceData02").text
            
            kaisai_match = re.search(r'(\d+)回\s*(\S+)\s*(\d+)日目', race_data02)
            if kaisai_match:
                info['venue'] = kaisai_match.group(2)
            else:
                info['venue'] = '不明'
            
            horses_match = re.search(r'(\d+)頭', race_data02)
            info['horse_count'] = int(horses_match.group(1)) if horses_match else 0
            
            logger.debug(f"Extracted: venue={info.get('venue')}, track={info.get('track_type')}, distance={info.get('distance')}")
            
        except Exception as e:
            logger.error(f"Error extracting race info: {e}")
            return {}
            
        return info
    
    def _update_database(self, race_id: str, race_data: Dict) -> bool:
        """データベースを更新"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            race_info = race_data.get('race_info', {})
            
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
            
            if cursor.rowcount > 0:
                logger.debug(f"Updated race_id={race_id}: {race_info.get('venue')}, {race_info.get('track_type')}, {race_info.get('distance')}m")
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


def scrape_race_detail(race_id: str, db_path: str = "data/keiba.db") -> bool:
    """
    単一のレース詳細を取得してDBを更新（バッチ処理用）
    
    Args:
        race_id: レースID
        db_path: データベースパス
        
    Returns:
        成功時True、失敗時False
    """
    scraper = RaceDetailScraperWithDB(db_path)
    
    try:
        success = scraper.scrape_and_update(race_id)
        return success
    finally:
        scraper.close_driver()


if __name__ == "__main__":
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # テスト
    test_race_id = "202508040411"
    logger.info(f"Testing with race_id: {test_race_id}")
    
    success = scrape_race_detail(test_race_id)
    
    if success:
        logger.success("✅ Test successful!")
    else:
        logger.error("❌ Test failed")
