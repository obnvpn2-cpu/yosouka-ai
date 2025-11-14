"""
予想家の予想履歴を取得するスクレイパー
"""
from typing import List, Dict, Optional
from backend.scraper.base import BaseScraper
from loguru import logger
from datetime import datetime
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup


class PredictionScraper(BaseScraper):
    """予想家の予想履歴を取得するスクレイパー"""
    
    def __init__(self):
        super().__init__()
        self.driver = None
    
    def _init_driver(self):
        """Seleniumドライバーを初期化"""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # ヘッドレスモード
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={self.session.headers["User-Agent"]}')
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("Selenium Chrome driver initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Chrome driver: {e}")
                raise
    
    def __del__(self):
        """デストラクタでドライバーを閉じる"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
    
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
            # Seleniumドライバーを初期化
            self._init_driver()
            
            logger.info(f"Loading page with Selenium: {url}")
            self.driver.get(url)
            
            # ページの読み込みを待機（最大10秒）
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "YosokaResultDetailList"))
                )
                logger.info("Page loaded successfully")
            except TimeoutException:
                logger.warning(f"Timeout waiting for page load: {url}")
            
            # 少し待機してJavaScriptの実行を待つ
            time.sleep(2)
            
            # ページソースを取得してBeautifulSoupでパース
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
        except Exception as e:
            logger.error(f"Error loading page with Selenium: {e}")
            return []
        
        predictions = []
        
        try:
            # 予想履歴のリストを探す
            # HTML構造: <div class="GensenYosoList"> > <ul> 内の <li> タグ
            prediction_elements = soup.select('div.GensenYosoList ul li')
            
            if not prediction_elements:
                logger.warning(f"No prediction elements found for predictor {predictor_id}")
                return []
            
            for element in prediction_elements[:limit]:
                try:
                    prediction = self._parse_prediction_element(element)
                    if prediction:
                        predictions.append(prediction)
                        logger.debug(f"Parsed prediction: {prediction.get('race_name', 'Unknown')}")
                    
                except Exception as e:
                    logger.warning(f"Error parsing prediction element: {e}")
                    continue
            
            logger.info(f"Found {len(predictions)} predictions for predictor {predictor_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error extracting predictions for predictor {predictor_id}: {e}")
            return []
        # Seleniumドライバーはプログラム終了時に一括終了するため、ここでは閉じない
    
    def _parse_prediction_element(self, element) -> Optional[Dict]:
        """予想要素を解析"""
        try:
            # 予想IDを <li> の id 属性から抽出（例: id="goods_state_5528852"）
            li_id = element.get('id', '')
            prediction_id = None
            if li_id.startswith('goods_state_'):
                prediction_id = int(li_id.replace('goods_state_', ''))
            
            # 的中/不的中の判定
            is_hit = 'NoHit' not in element.get('class', [])
            
            # レース情報を取得
            # 競馬場
            venue = None
            venue_element = element.find('span', class_='Jyo')
            if venue_element:
                venue = self.extract_text(venue_element)
            
            # レース番号
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
                
                # グレードを抽出（例: "アルゼンチン共和国杯(GII)" から "G2"）
                if '(G' in race_name_full or '(Ｇ' in race_name_full:
                    grade_match = re.search(r'\(G?Ｇ?([IⅠ123]+)\)', race_name_full)
                    if grade_match:
                        grade_num = grade_match.group(1)
                        # ローマ数字を数字に変換
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
                # "2025/11/08 12:17:48" のような形式
                date_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', td_text)
                if date_match:
                    year, month, day = date_match.groups()
                    race_date = datetime(int(year), int(month), int(day))
                    break
            
            # 本命馬を取得
            favorite_horse = None
            bamei_element = element.find('p', class_='Bamei')
            if bamei_element:
                # "◎ホーエリート（2番人気/6着）" のような形式
                bamei_text = self.extract_text(bamei_element)
                # ◎を除去して馬名を抽出
                horse_match = re.search(r'◎(.+?)（', bamei_text)
                if horse_match:
                    favorite_horse = horse_match.group(1).strip()
            
            # 払戻金を取得
            payout = 0
            payout_dds = element.find_all('dd')
            for dd in payout_dds:
                prev_dt = dd.find_previous_sibling('dt')
                if prev_dt and '払戻' in self.extract_text(prev_dt):
                    payout_text = self.extract_text(dd)
                    payout = self.extract_int(payout_text)
                    break
            
            # 収支を取得
            balance = 0
            for dd in payout_dds:
                prev_dt = dd.find_previous_sibling('dt')
                if prev_dt and '収支' in self.extract_text(prev_dt):
                    balance_text = self.extract_text(dd)
                    # マイナス記号を考慮
                    balance_text_clean = balance_text.replace(',', '').replace('円', '').strip()
                    try:
                        balance = int(balance_text_clean)
                    except ValueError:
                        balance = 0
                    break
            
            # 回収率を計算（払戻がある場合）
            roi = None
            if payout > 0 and balance != 0:
                # 収支 = 払戻 - 購入金額
                # 購入金額 = 払戻 - 収支
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
        """
        予想の詳細情報を取得
        
        Args:
            prediction_id: 予想ID
        
        Returns:
            予想の詳細情報
        """
        url = f"https://yoso.sp.netkeiba.com/?pid=yoso_detail&id={prediction_id}"
        
        soup = self.get_page(url)
        if not soup:
            logger.error(f"Failed to fetch prediction detail for ID {prediction_id}")
            return None
        
        try:
            detail = {}
            
            # レースID
            race_link = soup.find('a', href=lambda x: x and 'race_id=' in x)
            if race_link:
                race_id_match = re.search(r'race_id=(\d+)', race_link['href'])
                if race_id_match:
                    detail['race_id'] = race_id_match.group(1)
            
            # 本命、対抗、単穴
            # ※実際のHTML構造に応じて調整が必要
            favorite_element = soup.find(text=lambda t: t and '本命' in str(t))
            if favorite_element:
                # 本命馬の馬番を探す
                parent = favorite_element.find_parent()
                if parent:
                    horse_num = self.extract_int(self.extract_text(parent))
                    if horse_num:
                        detail['favorite_horse'] = horse_num
            
            # 買い目
            bet_element = soup.find(class_=lambda x: x and 'bet' in x.lower())
            if bet_element:
                detail['bet_horses'] = self.extract_text(bet_element)
            
            # コメント・見解
            comment_element = soup.find(class_=lambda x: x and 'comment' in x.lower())
            if comment_element:
                detail['comment'] = self.extract_text(comment_element)
            
            return detail
            
        except Exception as e:
            logger.error(f"Error parsing prediction detail for ID {prediction_id}: {e}")
            return None
