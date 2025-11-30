"""
レース詳細情報スクレイパー
race.netkeiba.com/race/result.html から詳細情報を取得
"""
import os
import sys
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger


class RaceDetailScraper:
    """レース詳細情報を取得するスクレイパー"""
    
    def __init__(self):
        """初期化"""
        self.driver = None
        self.wait = None
        
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
        
    def close_driver(self):
        """ドライバーを閉じる"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def get_race_details(self, race_id: str) -> Optional[Dict]:
        """
        レース詳細情報を取得
        
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
                
            self.driver.get(url)
            time.sleep(2)  # ページ読み込み待機
            
            # レース情報を取得
            race_info = self._extract_race_info()
            
            # レース結果を取得
            race_results = self._extract_race_results()
            
            # 払い戻し情報を取得
            payback_info = self._extract_payback_info()
            
            # コーナー通過順を取得
            corner_pass = self._extract_corner_pass()
            
            # ラップタイムを取得
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
            # レース名
            race_name_elem = self.driver.find_element(By.CLASS_NAME, "RaceName")
            info['race_name'] = race_name_elem.text.strip().split('\n')[0]
            
            # グレード（G1/G2/G3など）
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
                
            # レース条件（RaceData01）
            race_data01 = self.driver.find_element(By.CLASS_NAME, "RaceData01").text
            
            # 発走時刻
            time_match = re.search(r'(\d{1,2}:\d{2})発走', race_data01)
            info['post_time'] = time_match.group(1) if time_match else None
            
            # 距離・トラック
            distance_match = re.search(r'(芝|ダート)(\d+)m', race_data01)
            if distance_match:
                info['track_type'] = distance_match.group(1)
                info['distance'] = int(distance_match.group(2))
            else:
                info['track_type'] = '不明'
                info['distance'] = 0
                
            # 天候
            weather_match = re.search(r'天候:([^\s]+)', race_data01)
            info['weather'] = weather_match.group(1) if weather_match else None
            
            # 馬場状態
            track_condition_match = re.search(r'馬場:([^\s]+)', race_data01)
            info['track_condition'] = track_condition_match.group(1) if track_condition_match else None
            
            # レース詳細（RaceData02）
            race_data02 = self.driver.find_element(By.CLASS_NAME, "RaceData02").text
            
            # 開催情報（例：5回東京2日目）
            kaisai_match = re.search(r'(\d+)回\s*(\S+)\s*(\d+)日目', race_data02)
            if kaisai_match:
                info['kaisai_count'] = int(kaisai_match.group(1))
                info['venue'] = kaisai_match.group(2)
                info['day'] = int(kaisai_match.group(3))
            else:
                info['venue'] = '不明'
                
            # 条件（例：サラ系３歳以上）
            condition_match = re.search(r'(サラ系|アラブ系)([^\s]+)', race_data02)
            info['race_condition'] = condition_match.group(0) if condition_match else None
            
            # クラス（例：オープン）
            class_match = re.search(r'(オープン|1600万|1000万|500万|未勝利|新馬)', race_data02)
            info['race_class'] = class_match.group(1) if class_match else None
            
            # 負担重量（例：ハンデ、定量、別定）
            weight_match = re.search(r'(ハンデ|定量|別定)', race_data02)
            info['weight_type'] = weight_match.group(1) if weight_match else None
            
            # 頭数
            horses_match = re.search(r'(\d+)頭', race_data02)
            info['horse_count'] = int(horses_match.group(1)) if horses_match else 0
            
            # 賞金
            prize_match = re.search(r'本賞金:([\d,]+)万円', race_data02)
            if prize_match:
                # 最初の賞金（1着賞金）を取得
                info['prize_money'] = int(prize_match.group(1).replace(',', ''))
            else:
                info['prize_money'] = 0
                
        except Exception as e:
            logger.error(f"Error extracting race info: {e}")
            
        return info
        
    def _extract_race_results(self) -> List[Dict]:
        """レース結果（各馬の情報）を抽出"""
        results = []
        
        try:
            # 結果テーブルを取得
            table = self.driver.find_element(By.CLASS_NAME, "RaceTable01")
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr.HorseList")
            
            for row in rows:
                try:
                    result = {}
                    
                    # 着順
                    rank_elem = row.find_element(By.CLASS_NAME, "Result_Num")
                    result['rank'] = int(rank_elem.text.strip())
                    
                    # 枠番
                    waku_elem = row.find_element(By.CSS_SELECTOR, "td.Num.Waku1, td.Num.Waku2, td.Num.Waku3, td.Num.Waku4, td.Num.Waku5, td.Num.Waku6, td.Num.Waku7, td.Num.Waku8")
                    result['bracket'] = int(waku_elem.text.strip())
                    
                    # 馬番
                    horse_num_elem = row.find_element(By.CSS_SELECTOR, "td.Num.Txt_C")
                    result['horse_number'] = int(horse_num_elem.text.strip())
                    
                    # 馬名
                    horse_name_elem = row.find_element(By.CLASS_NAME, "Horse_Name")
                    result['horse_name'] = horse_name_elem.text.strip()
                    
                    # 性齢（例：セ7）
                    sex_age_elem = row.find_element(By.CSS_SELECTOR, "td.Horse_Info.Txt_C span")
                    result['sex_age'] = sex_age_elem.text.strip()
                    
                    # 斤量
                    weight_elem = row.find_element(By.CLASS_NAME, "JockeyWeight")
                    result['jockey_weight'] = float(weight_elem.text.strip())
                    
                    # 騎手
                    jockey_elem = row.find_element(By.CLASS_NAME, "Jockey")
                    result['jockey'] = jockey_elem.text.strip()
                    
                    # タイム
                    time_elem = row.find_element(By.CLASS_NAME, "RaceTime")
                    result['time'] = time_elem.text.strip()
                    
                    # 着差
                    time_elems = row.find_elements(By.CLASS_NAME, "Time")
                    if len(time_elems) > 1:
                        result['margin'] = time_elems[1].text.strip()
                    else:
                        result['margin'] = ""
                        
                    # 人気
                    odds_people_elem = row.find_element(By.CLASS_NAME, "OddsPeople")
                    result['popularity'] = int(odds_people_elem.text.strip())
                    
                    # 単勝オッズ
                    odds_elems = row.find_elements(By.CSS_SELECTOR, "td.Odds")
                    if len(odds_elems) > 1:
                        odds_text = odds_elems[1].text.strip()
                        result['odds'] = float(odds_text) if odds_text else 0.0
                    else:
                        result['odds'] = 0.0
                        
                    # 後3F
                    passage_elems = row.find_elements(By.CLASS_NAME, "Time")
                    if len(passage_elems) > 2:
                        result['last_3f'] = passage_elems[2].text.strip()
                    else:
                        result['last_3f'] = ""
                        
                    # コーナー通過順
                    try:
                        passage_elem = row.find_element(By.CLASS_NAME, "PassageRate")
                        result['corner_pass'] = passage_elem.text.strip()
                    except NoSuchElementException:
                        result['corner_pass'] = ""
                        
                    # 厩舎
                    trainer_elem = row.find_element(By.CLASS_NAME, "Trainer")
                    trainer_text = trainer_elem.text.strip()
                    # 「栗東 小林」→「栗東」と「小林」に分割
                    trainer_parts = trainer_text.split('\n')
                    if len(trainer_parts) >= 2:
                        result['trainer_location'] = trainer_parts[0]
                        result['trainer_name'] = trainer_parts[1]
                    else:
                        result['trainer_location'] = ""
                        result['trainer_name'] = trainer_text
                        
                    # 馬体重
                    weight_elem = row.find_element(By.CLASS_NAME, "Weight")
                    weight_text = weight_elem.text.strip()
                    # 「500(-2)」→「500」と「-2」に分割
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
            # 払い戻しテーブルを取得
            payback_wrapper = self.driver.find_element(By.CLASS_NAME, "ResultPaybackLeftWrap")
            tables = payback_wrapper.find_elements(By.CLASS_NAME, "Payout_Detail_Table")
            
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows:
                    try:
                        # 券種（例：単勝、複勝、馬連など）
                        th = row.find_element(By.TAG_NAME, "th")
                        bet_type = th.text.strip()
                        
                        # 結果（馬番）
                        result_td = row.find_element(By.CLASS_NAME, "Result")
                        result_text = result_td.text.strip()
                        
                        # 払戻金
                        payout_td = row.find_element(By.CLASS_NAME, "Payout")
                        payout_text = payout_td.text.strip()
                        
                        # 人気
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
            # コーナー通過順テーブルを取得
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
            'cumulative': [],  # 累積タイム
            'intervals': []     # 区間タイム（ハロン）
        }
        
        try:
            # ラップタイムテーブルを取得
            lap_table = self.driver.find_element(By.CLASS_NAME, "Race_HaronTime")
            rows = lap_table.find_elements(By.CSS_SELECTOR, "tbody tr.HaronTime")
            
            if len(rows) >= 2:
                # 1行目：累積タイム
                cumulative_cells = rows[0].find_elements(By.TAG_NAME, "td")
                lap_times['cumulative'] = [cell.text.strip() for cell in cumulative_cells]
                
                # 2行目：区間タイム
                interval_cells = rows[1].find_elements(By.TAG_NAME, "td")
                lap_times['intervals'] = [cell.text.strip() for cell in interval_cells]
                
            # ペース情報
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
    logger.info("Starting race detail scraper test...")
    
    scraper = RaceDetailScraper()
    
    try:
        # テスト用レースID
        test_race_id = "202505050211"  # アルゼンチン共和国杯(G2)
        
        logger.info(f"Testing with race_id: {test_race_id}")
        
        result = scraper.get_race_details(test_race_id)
        
        if result:
            logger.success("✅ Scraping successful!")
            logger.info(f"Race name: {result['race_info'].get('race_name')}")
            logger.info(f"Grade: {result['race_info'].get('grade')}")
            logger.info(f"Distance: {result['race_info'].get('distance')}m")
            logger.info(f"Track: {result['race_info'].get('track_type')}")
            logger.info(f"Horses: {len(result['race_results'])} horses")
            logger.info(f"Payback types: {list(result['payback'].keys())}")
            
            # 詳細をJSONで出力
            import json
            output_file = f"race_{test_race_id}_details.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Details saved to: {output_file}")
            
        else:
            logger.error("❌ Scraping failed")
            
    except Exception as e:
        logger.exception(f"Test failed: {e}")
        
    finally:
        scraper.close_driver()


if __name__ == "__main__":
    # ログ設定
    logger.add("logs/race_detail_scraper_{time}.log", rotation="1 day", retention="7 days")
    
    test_scraper()
