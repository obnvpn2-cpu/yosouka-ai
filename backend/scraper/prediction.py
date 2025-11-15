"""
予想家の予想履歴を取得するスクレイパー（最終安定版 - ベストプラクティス適用）
"""
from typing import List, Dict, Optional
from backend.scraper.base import BaseScraper
from loguru import logger
from datetime import datetime
import re
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException
)
from bs4 import BeautifulSoup


class PredictionScraper(BaseScraper):
    """予想家の予想履歴を取得するスクレイパー"""
    
    def __init__(self):
        super().__init__()
        self.driver = None
        self.retry_count = 3  # リトライ回数
    
    def _cleanup_chrome_processes(self):
        """Chrome関連プロセスを完全にクリーンアップ"""
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
    
    def _init_driver(self):
        """Seleniumドライバーを初期化"""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--proxy-server="direct://"')
            chrome_options.add_argument('--proxy-bypass-list=*')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument(f'user-agent={self.session.headers["User-Agent"]}')
            chrome_options.add_argument('--remote-debugging-port=0')
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                # 暗黙的な待機を設定（全てのfind_element処理に適用）
                self.driver.implicitly_wait(10)
                logger.info("Selenium Chrome driver initialized with implicit wait")
            except Exception as e:
                logger.error(f"Failed to initialize Chrome driver: {e}")
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
            
            time.sleep(3)
            self._cleanup_chrome_processes()
            time.sleep(3)
            logger.debug("Driver safely closed")
    
    def __del__(self):
        """デストラクタでドライバーを閉じる"""
        self._safe_quit_driver()
    
    def _wait_for_element(self, by, value, timeout=30):
        """要素が表示されるまで明示的に待機（リトライ機能付き）"""
        last_error = None
        
        for attempt in range(self.retry_count):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, value))
                )
                logger.debug(f"Element found: {value}")
                return element
            except TimeoutException as e:
                last_error = e
                logger.warning(f"Timeout waiting for element (attempt {attempt + 1}/{self.retry_count}): {value}")
                time.sleep(2)
            except NoSuchElementException as e:
                last_error = e
                logger.warning(f"Element not found (attempt {attempt + 1}/{self.retry_count}): {value}")
                time.sleep(2)
            except StaleElementReferenceException as e:
                last_error = e
                logger.warning(f"Stale element (attempt {attempt + 1}/{self.retry_count}): {value}")
                time.sleep(2)
        
        logger.error(f"Failed to find element after {self.retry_count} attempts: {value}")
        return None
    
    def _click_element_safely(self, by, value, timeout=30):
        """要素を安全にクリック（リトライ機能付き）"""
        last_error = None
        
        for attempt in range(self.retry_count):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                )
                element.click()
                logger.debug(f"Element clicked: {value}")
                return True
            except TimeoutException as e:
                last_error = e
                logger.warning(f"Timeout clicking element (attempt {attempt + 1}/{self.retry_count}): {value}")
                time.sleep(2)
            except ElementClickInterceptedException as e:
                last_error = e
                logger.warning(f"Click intercepted (attempt {attempt + 1}/{self.retry_count}): {value}")
                # JavaScriptで直接クリックを試みる
                try:
                    element = self.driver.find_element(by, value)
                    self.driver.execute_script("arguments[0].click();", element)
                    logger.debug(f"Element clicked via JavaScript: {value}")
                    return True
                except Exception as js_error:
                    logger.warning(f"JavaScript click also failed: {js_error}")
                time.sleep(2)
        
        logger.error(f"Failed to click element after {self.retry_count} attempts: {value}")
        return False
    
    def get_predictor_predictions(self, predictor_id: int, limit: int = 50) -> List[Dict]:
        """
        予想家の予想履歴を取得（最新50件）
        
        Args:
            predictor_id: 予想家のID
            limit: 取得する予想の最大数
        
        Returns:
            予想情報のリスト
        """
        url = f"https://yoso.sp.netkeiba.com/yosoka/jra/profile.html?id={predictor_id}"
        
        try:
            # 既存のドライバーを完全に終了
            self._safe_quit_driver()
            
            # 新しいドライバーを初期化
            self._init_driver()
            
            logger.info(f"Loading page with Selenium: {url}")
            self.driver.get(url)
            
            # ページの読み込みを待機（明示的な待機）
            gensenlist_element = self._wait_for_element(
                By.CLASS_NAME, 
                "GensenYosoList", 
                timeout=10
            )
            
            if not gensenlist_element:
                logger.warning(f"GensenYosoList not found for predictor {predictor_id}")
                return []
            
            logger.info("Page loaded successfully")
            
            # 「新着」タブをクリック
            new_tab_clicked = self._click_element_safely(
                By.LINK_TEXT,
                "新着",
                timeout=5
            )
            
            if new_tab_clicked:
                logger.info("Clicked '新着' tab")
                time.sleep(3)
            else:
                logger.warning("Could not click '新着' tab, using default view")
            
            # JavaScript実行待機
            time.sleep(10)
            
            # ページソースを取得してBeautifulSoupでパース
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
        except WebDriverException as e:
            logger.error(f"WebDriver error for predictor {predictor_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading page with Selenium: {e}")
            return []
        finally:
            # 処理が終わったら必ずドライバーを終了
            self._safe_quit_driver()
        
        predictions = []
        
        try:
            # 予想履歴のリストを探す
            prediction_elements = soup.select('div.GensenYosoList ul li.Selectable')
            
            if not prediction_elements:
                logger.warning(f"No prediction elements found for predictor {predictor_id}")
                return []
            
            logger.info(f"Found {len(prediction_elements)} prediction elements")
            
            for element in prediction_elements[:limit]:
                try:
                    prediction = self._parse_prediction_element(element)
                    if prediction:
                        predictions.append(prediction)
                        logger.debug(f"Parsed prediction: {prediction.get('race_name', 'Unknown')}")
                    
                except Exception as e:
                    logger.warning(f"Error parsing prediction element: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(predictions)} predictions for predictor {predictor_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error extracting predictions for predictor {predictor_id}: {e}")
            return []
    
    def _parse_prediction_element(self, element) -> Optional[Dict]:
        """予想要素を解析"""
        try:
            # 予想IDを <li> の id 属性から抽出
            li_id = element.get('id', '')
            prediction_id = None
            if li_id.startswith('goods_state_'):
                prediction_id = int(li_id.replace('goods_state_', ''))
            
            # 的中/不的中の判定
            li_classes = element.get('class', [])
            is_hit = 'Hit' in li_classes
            
            # レース情報を取得
            venue = None
            venue_element = element.find('span', class_='Jyo')
            if venue_element:
                venue = self.extract_text(venue_element)
            
            race_num = None
            num_element = element.find('span', class_='Num')
            if num_element:
                race_num = self.extract_text(num_element)
            
            # レース名（グレードを含む）
            race_name = None
            grade = None
            name_element = element.find('span', class_='Name')
            if name_element:
                race_name_full = self.extract_text(name_element)
                race_name = race_name_full
                
                # グレードを抽出
                if '(G' in race_name_full or '(Ｇ' in race_name_full:
                    grade_match = re.search(r'\(G?Ｇ?([IⅠ123]+)\)', race_name_full)
                    if grade_match:
                        grade_num = grade_match.group(1)
                        if grade_num in ['I', 'Ⅰ', '1']:
                            grade = 'G1'
                        elif grade_num in ['II', 'Ⅱ', '2']:
                            grade = 'G2'
                        elif grade_num in ['III', 'Ⅲ', '3']:
                            grade = 'G3'
            
            # 公開日時を取得
            race_date = None
            date_elements = element.find_all('td')
            for td in date_elements:
                td_text = self.extract_text(td)
                date_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', td_text)
                if date_match:
                    year, month, day = date_match.groups()
                    race_date = datetime(int(year), int(month), int(day))
                    break
            
            # 本命馬を取得
            favorite_horse = None
            bamei_element = element.find('p', class_='Bamei')
            if bamei_element:
                bamei_text = self.extract_text(bamei_element)
                horse_match = re.search(r'◎(.+?)（', bamei_text)
                if horse_match:
                    favorite_horse = horse_match.group(1).strip()
            
            # 払戻金を取得
            payout = 0
            balance_area = element.find('div', class_='BalanceArea')
            if balance_area:
                payout_dds = balance_area.find_all('dd')
                for dd in payout_dds:
                    prev_dt = dd.find_previous_sibling('dt')
                    if prev_dt and '払戻' in self.extract_text(prev_dt):
                        payout_text = self.extract_text(dd)
                        em_tag = dd.find('em')
                        if em_tag:
                            payout_text = self.extract_text(em_tag)
                        payout = self.extract_int(payout_text)
                        break
            
            # 収支を取得
            balance = 0
            if balance_area:
                balance_dds = balance_area.find_all('dd')
                for dd in balance_dds:
                    prev_dt = dd.find_previous_sibling('dt')
                    if prev_dt and '収支' in self.extract_text(prev_dt):
                        balance_text = self.extract_text(dd)
                        em_tag = dd.find('em')
                        if em_tag:
                            balance_text = self.extract_text(em_tag)
                        balance_text_clean = balance_text.replace(',', '').replace('円', '').strip()
                        try:
                            balance = int(balance_text_clean)
                        except ValueError:
                            balance = 0
                        break
            
            # 回収率を計算
            roi = None
            if payout > 0 and balance != 0:
                purchase_amount = payout - balance
                if purchase_amount > 0:
                    roi = (payout / purchase_amount) * 100
            
            prediction_info = {
                'prediction_id': prediction_id,
                'race_name': race_name,
                'race_date': race_date,
                'venue': venue,
                'race_num': race_num,
                'grade': grade,
                'favorite_horse': favorite_horse,
                'is_hit': is_hit,
                'payout': payout,
                'balance': balance,
                'roi': roi
            }
            
            return prediction_info
            
        except Exception as e:
            logger.warning(f"Error in _parse_prediction_element: {e}")
            return None
    
    def get_prediction_detail(self, prediction_id: int) -> Optional[Dict]:
        """予想の詳細情報を取得"""
        url = f"https://yoso.sp.netkeiba.com/?pid=yoso_detail&id={prediction_id}"
        
        soup = self.get_page(url)
        if not soup:
            logger.error(f"Failed to fetch prediction detail for ID {prediction_id}")
            return None
        
        try:
            detail = {}
            
            race_link = soup.find('a', href=lambda x: x and 'race_id=' in x)
            if race_link:
                race_id_match = re.search(r'race_id=(\d+)', race_link['href'])
                if race_id_match:
                    detail['race_id'] = race_id_match.group(1)
            
            favorite_element = soup.find(text=lambda t: t and '本命' in str(t))
            if favorite_element:
                parent = favorite_element.find_parent()
                if parent:
                    horse_num = self.extract_int(self.extract_text(parent))
                    if horse_num:
                        detail['favorite_horse'] = horse_num
            
            bet_element = soup.find(class_=lambda x: x and 'bet' in x.lower())
            if bet_element:
                detail['bet_horses'] = self.extract_text(bet_element)
            
            comment_element = soup.find(class_=lambda x: x and 'comment' in x.lower())
            if comment_element:
                detail['comment'] = self.extract_text(comment_element)
            
            return detail
            
        except Exception as e:
            logger.error(f"Error parsing prediction detail for ID {prediction_id}: {e}")
            return None
