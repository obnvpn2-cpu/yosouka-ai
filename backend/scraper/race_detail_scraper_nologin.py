"""
レース詳細情報スクレイパー（ログインなし版）
ログイン不要な情報のみ取得
"""
import os
import sys
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from loguru import logger


class RaceDetailScraper:
    """レース詳細情報を取得するスクレイパー（ログインなし）"""
    
    def __init__(self, chromedriver_path=None):
        """初期化"""
        self.driver = None
        self.wait = None
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
            
            logger.info(f"Using ChromeDriver at: {driver_path}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 15)
            logger.success("ChromeDriver setup completed!")
            
        except Exception as e:
            logger.error(f"Failed to setup ChromeDriver: {e}")
            raise
        
    def close_driver(self):
        """ドライバーを閉じる"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def get_race_details(self, race_id: str) -> Optional[Dict]:
        """
        レース詳細情報を取得（ログインなし）
        
        Args:
            race_id: レースID (例: 202505050211)
            
        Returns:
            レース詳細情報の辞書、エラー時はNone
        """
        url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}"
        logger.info(f"Fetching race details: {url}")
        
        try:
            if not self.driver:
                self.setup_driver()
                
            # ログインなしで直接アクセス
            self.driver.get(url)
            time.sleep(2)
            
            race_info = self._extract_race_info()
            race_results = self._extract_race_results()
            payback_info = self._extract_payback_info()
            corner_pass = self._extract_corner_pass()
            lap_times = self._extract_lap_times()
            
            return {
                'race_id': race_id,
                'race_info': race_info,
                'race_results': race_results,
                'payback': payback_info,
                'corner_pass': corner_pass,
                'lap_times': lap_times,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching race {race_id}: {e}")
            return None
            
    def _extract_race_info(self) -> Dict:
        """レース基本情報を抽出"""
        info = {}
        
        try:
            race_name_elem = self.driver.find_element(By.CLASS_NAME, "RaceName")
            info['race_name'] = race_name_elem.text.strip().split('\n')[0]
            
            try:
                grade_elem = race_name_elem.find_element(By.CSS_SELECTOR, "[class*='Icon_GradeType']")
                grade_class = grade_elem.get_attribute('class')
                if 'Icon_GradeType1' in grade_class:
                    info['grade'] = 'G1'
                elif 'Icon_GradeType2' in grade_class:
                    info['grade'] = 'G2'
                elif 'Icon_GradeType3' in grade_class:
                    info['grade'] = 'G3'
                else:
                    info['grade'] = None
            except NoSuchElementException:
                info['grade'] = None
                
            race_data01 = self.driver.find_element(By.CLASS_NAME, "RaceData01").text
            
            time_match = re.search(r'(\d{1,2}:\d{2})発走', race_data01)
            info['post_time'] = time_match.group(1) if time_match else None
            
            distance_match = re.search(r'(芝|ダート)(\d+)m', race_data01)
            if distance_match:
                info['track_type'] = distance_match.group(1)
                info['distance'] = int(distance_match.group(2))
            else:
                info['track_type'] = '不明'
                info['distance'] = 0
                
            weather_match = re.search(r'天候:([^\s]+)', race_data01)
            info['weather'] = weather_match.group(1) if weather_match else None
            
            track_condition_match = re.search(r'馬場:([^\s]+)', race_data01)
            info['track_condition'] = track_condition_match.group(1) if track_condition_match else None
            
            race_data02 = self.driver.find_element(By.CLASS_NAME, "RaceData02").text
            
            kaisai_match = re.search(r'(\d+)回\s*(\S+)\s*(\d+)日目', race_data02)
            if kaisai_match:
                info['kaisai_count'] = int(kaisai_match.group(1))
                info['venue'] = kaisai_match.group(2)
                info['day'] = int(kaisai_match.group(3))
            else:
                info['venue'] = '不明'
                
            condition_match = re.search(r'(サラ系|アラブ系)([^\s]+)', race_data02)
            info['race_condition'] = condition_match.group(0) if condition_match else None
            
            class_match = re.search(r'(オープン|1600万|1000万|500万|未勝利|新馬)', race_data02)
            info['race_class'] = class_match.group(1) if class_match else None
            
            weight_match = re.search(r'(ハンデ|定量|別定)', race_data02)
            info['weight_type'] = weight_match.group(1) if weight_match else None
            
            horses_match = re.search(r'(\d+)頭', race_data02)
            info['horse_count'] = int(horses_match.group(1)) if horses_match else 0
            
            prize_match = re.search(r'本賞金:([\d,]+)万円', race_data02)
            if prize_match:
                info['prize_money'] = int(prize_match.group(1).replace(',', ''))
            else:
                info['prize_money'] = 0
                
        except Exception as e:
            logger.error(f"Error extracting race info: {e}")
            
        return info
        
    def _extract_race_results(self) -> List[Dict]:
        """レース結果を抽出"""
        results = []
        
        try:
            table = self.driver.find_element(By.CLASS_NAME, "RaceTable01")
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr.HorseList")
            
            for row in rows:
                try:
                    result = {}
                    
                    rank_elem = row.find_element(By.CLASS_NAME, "Result_Num")
                    result['rank'] = int(rank_elem.text.strip())
                    
                    waku_elem = row.find_element(By.CSS_SELECTOR, "td.Num.Waku1, td.Num.Waku2, td.Num.Waku3, td.Num.Waku4, td.Num.Waku5, td.Num.Waku6, td.Num.Waku7, td.Num.Waku8")
                    result['bracket'] = int(waku_elem.text.strip())
                    
                    horse_num_elem = row.find_element(By.CSS_SELECTOR, "td.Num.Txt_C")
                    result['horse_number'] = int(horse_num_elem.text.strip())
                    
                    horse_name_elem = row.find_element(By.CLASS_NAME, "Horse_Name")
                    result['horse_name'] = horse_name_elem.text.strip()
                    
                    sex_age_elem = row.find_element(By.CSS_SELECTOR, "td.Horse_Info.Txt_C span")
                    result['sex_age'] = sex_age_elem.text.strip()
                    
                    weight_elem = row.find_element(By.CLASS_NAME, "JockeyWeight")
                    result['jockey_weight'] = float(weight_elem.text.strip())
                    
                    jockey_elem = row.find_element(By.CLASS_NAME, "Jockey")
                    result['jockey'] = jockey_elem.text.strip()
                    
                    time_elem = row.find_element(By.CLASS_NAME, "RaceTime")
                    result['time'] = time_elem.text.strip()
                    
                    time_elems = row.find_elements(By.CLASS_NAME, "Time")
                    if len(time_elems) > 1:
                        result['margin'] = time_elems[1].text.strip()
                    else:
                        result['margin'] = ""
                        
                    odds_people_elem = row.find_element(By.CLASS_NAME, "OddsPeople")
                    result['popularity'] = int(odds_people_elem.text.strip())
                    
                    odds_elems = row.find_elements(By.CSS_SELECTOR, "td.Odds")
                    if len(odds_elems) > 1:
                        odds_text = odds_elems[1].text.strip()
                        result['odds'] = float(odds_text) if odds_text else 0.0
                    else:
                        result['odds'] = 0.0
                        
                    passage_elems = row.find_elements(By.CLASS_NAME, "Time")
                    if len(passage_elems) > 2:
                        result['last_3f'] = passage_elems[2].text.strip()
                    else:
                        result['last_3f'] = ""
                        
                    try:
                        passage_elem = row.find_element(By.CLASS_NAME, "PassageRate")
                        result['corner_pass'] = passage_elem.text.strip()
                    except NoSuchElementException:
                        result['corner_pass'] = ""
                        
                    trainer_elem = row.find_element(By.CLASS_NAME, "Trainer")
                    trainer_text = trainer_elem.text.strip()
                    trainer_parts = trainer_text.split('\n')
                    if len(trainer_parts) >= 2:
                        result['trainer_location'] = trainer_parts[0]
                        result['trainer_name'] = trainer_parts[1]
                    else:
                        result['trainer_location'] = ""
                        result['trainer_name'] = trainer_text
                        
                    weight_elem = row.find_element(By.CLASS_NAME, "Weight")
                    weight_text = weight_elem.text.strip()
                    weight_match = re.search(r'(\d+)\(([+-]?\d+)\)', weight_text)
                    if weight_match:
                        result['horse_weight'] = int(weight_match.group(1))
                        result['weight_change'] = int(weight_match.group(2))
                    else:
                        result['horse_weight'] = 0
                        result['weight_change'] = 0
                        
                    results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Error extracting horse result: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting race results: {e}")
            
        return results
        
    def _extract_payback_info(self) -> Dict:
        """払い戻し情報を抽出"""
        payback = {}
        
        try:
            payback_wrapper = self.driver.find_element(By.CLASS_NAME, "ResultPaybackLeftWrap")
            tables = payback_wrapper.find_elements(By.CLASS_NAME, "Payout_Detail_Table")
            
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows:
                    try:
                        th = row.find_element(By.TAG_NAME, "th")
                        bet_type = th.text.strip()
                        
                        result_td = row.find_element(By.CLASS_NAME, "Result")
                        result_text = result_td.text.strip()
                        
                        payout_td = row.find_element(By.CLASS_NAME, "Payout")
                        payout_text = payout_td.text.strip()
                        
                        ninki_td = row.find_element(By.CLASS_NAME, "Ninki")
                        ninki_text = ninki_td.text.strip()
                        
                        payback[bet_type] = {
                            'result': result_text,
                            'payout': payout_text,
                            'popularity': ninki_text
                        }
                        
                    except Exception as e:
                        logger.warning(f"Error extracting payback row: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error extracting payback info: {e}")
            
        return payback
        
    def _extract_corner_pass(self) -> Dict:
        """コーナー通過順を抽出"""
        corner_pass = {}
        
        try:
            corner_table = self.driver.find_element(By.CSS_SELECTOR, "table.Corner_Num")
            rows = corner_table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                try:
                    th = row.find_element(By.TAG_NAME, "th")
                    corner_name = th.text.strip()
                    
                    td = row.find_element(By.TAG_NAME, "td")
                    pass_order = td.text.strip()
                    
                    corner_pass[corner_name] = pass_order
                    
                except Exception as e:
                    logger.warning(f"Error extracting corner pass row: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting corner pass: {e}")
            
        return corner_pass
        
    def _extract_lap_times(self) -> Dict:
        """ラップタイムを抽出"""
        lap_times = {
            'cumulative': [],
            'intervals': []
        }
        
        try:
            lap_table = self.driver.find_element(By.CLASS_NAME, "Race_HaronTime")
            rows = lap_table.find_elements(By.CSS_SELECTOR, "tbody tr.HaronTime")
            
            if len(rows) >= 2:
                cumulative_cells = rows[0].find_elements(By.TAG_NAME, "td")
                lap_times['cumulative'] = [cell.text.strip() for cell in cumulative_cells]
                
                interval_cells = rows[1].find_elements(By.TAG_NAME, "td")
                lap_times['intervals'] = [cell.text.strip() for cell in interval_cells]
                
            try:
                pace_elem = self.driver.find_element(By.CSS_SELECTOR, ".RapPace_Title span")
                lap_times['pace'] = pace_elem.text.strip()
            except NoSuchElementException:
                lap_times['pace'] = None
                
        except Exception as e:
            logger.error(f"Error extracting lap times: {e}")
            
        return lap_times


def test_scraper():
    """スクレイパーのテスト"""
    logger.info("=" * 70)
    logger.info("��� レース詳細スクレイパー テスト開始（ログインなし版）")
    logger.info("=" * 70)
    
    scraper = RaceDetailScraper()
    
    try:
        test_race_id = "202505050211"
        
        logger.info(f"��� テスト対象: race_id={test_race_id}")
        logger.info("")
        
        result = scraper.get_race_details(test_race_id)
        
        if result:
            logger.success("=" * 70)
            logger.success("✅ スクレイピング成功！")
            logger.success("=" * 70)
            logger.info(f"��� レース名: {result['race_info'].get('race_name')}")
            logger.info(f"��� グレード: {result['race_info'].get('grade')}")
            logger.info(f"��� 距離: {result['race_info'].get('distance')}m")
            logger.info(f"��� トラック: {result['race_info'].get('track_type')}")
            logger.info(f"��� 出走頭数: {len(result['race_results'])}頭")
            logger.info(f"��� 払戻種類: {len(result['payback'])}種類")
            logger.info("")
            
            # 保存先ディレクトリを作成
            project_root = Path(__file__).resolve().parent.parent.parent
            output_dir = project_root / "data" / "race_details"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            import json
            output_file = output_dir / f"race_{test_race_id}_details.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.success(f"��� 詳細データ保存: {output_file}")
            logger.info("")
            logger.info("=" * 70)
            logger.success("��� テスト完了！")
            logger.info("=" * 70)
            
        else:
            logger.error("=" * 70)
            logger.error("❌ スクレイピング失敗")
            logger.error("=" * 70)
            
    except Exception as e:
        logger.exception(f"テスト中にエラーが発生: {e}")
        
    finally:
        scraper.close_driver()


if __name__ == "__main__":
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # ログディレクトリ作成
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(log_dir / "race_detail_scraper_{time}.log", rotation="1 day", retention="7 days")
    
    test_scraper()
