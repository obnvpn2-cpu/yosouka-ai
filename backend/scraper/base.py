"""
スクレイピングのベースクラス
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import Optional
from backend.config import settings
from loguru import logger


class BaseScraper:
    """スクレイピングのベースクラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.delay = settings.scraping_delay
        self.max_retries = settings.max_retries
        self.timeout = settings.request_timeout
        self.is_logged_in = False
    
    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """netkeibaにログイン"""
        username = username or settings.netkeiba_username
        password = password or settings.netkeiba_password
        
        if not username or not password:
            logger.warning("netkeiba credentials not provided. Some features may be limited.")
            return False
        
        try:
            # ログインページにアクセス
            login_url = "https://regist.netkeiba.com/account/?pid=login"
            response = self.session.get(login_url, timeout=self.timeout)
            
            # ログイン情報を送信
            login_data = {
                'login_id': username,
                'pswd': password,
                'url': ''
            }
            
            post_url = "https://regist.netkeiba.com/account/?pid=login&action=auth"
            response = self.session.post(post_url, data=login_data, timeout=self.timeout)
            
            # ログイン成功チェック（簡易版）
            if response.status_code == 200:
                self.is_logged_in = True
                logger.info("Successfully logged in to netkeiba")
                return True
            else:
                logger.error(f"Login failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def get_page(self, url: str, encoding: str = 'euc-jp') -> Optional[BeautifulSoup]:
        """
        ページを取得してBeautifulSoupオブジェクトを返す
        
        Args:
            url: 取得するURL
            encoding: 文字エンコーディング（デフォルト: euc-jp）
        
        Returns:
            BeautifulSoupオブジェクト、失敗時はNone
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.session.get(url, timeout=self.timeout)
                response.encoding = encoding
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # リクエスト間隔を守る
                    time.sleep(self.delay)
                    
                    return soup
                else:
                    logger.warning(f"Status code {response.status_code} for {url}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout error for {url} (attempt {attempt + 1})")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
            
            # リトライ前に待機
            if attempt < self.max_retries - 1:
                wait_time = self.delay * (attempt + 1)
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None
    
    def extract_text(self, element, default: str = "") -> str:
        """要素からテキストを安全に抽出"""
        if element:
            return element.get_text(strip=True)
        return default
    
    def extract_int(self, text: str, default: int = 0) -> int:
        """文字列から整数を抽出"""
        try:
            # カンマや全角数字を除去して変換
            cleaned = ''.join(c for c in text if c.isdigit())
            return int(cleaned) if cleaned else default
        except ValueError:
            return default
    
    def extract_float(self, text: str, default: float = 0.0) -> float:
        """文字列から浮動小数点数を抽出"""
        try:
            # カンマを除去して変換
            cleaned = text.replace(',', '').replace('%', '')
            return float(cleaned) if cleaned else default
        except ValueError:
            return default
