"""
デバッグ用スクレイパー（ブラウザを表示してログイン確認）
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from loguru import logger
from dotenv import load_dotenv


def debug_login():
    """ログインプロセスをデバッグ"""
    load_dotenv()
    username = os.getenv('NETKEIBA_USERNAME')
    password = os.getenv('NETKEIBA_PASSWORD')
    
    if not username or not password:
        logger.error("認証情報が.envにありません")
        return
    
    logger.info(f"Username: {username}")
    logger.info(f"Password: {'*' * len(password)}")
    
    # ヘッドレスモードOFF（ブラウザが表示される）
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # コメントアウト
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    driver_path = os.path.join(project_root, 'drivers', 'chromedriver.exe')
    
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        logger.info("ログインページにアクセス...")
        return_url = "https://race.netkeiba.com/race/result.html?race_id=202505050211"
        login_url = f"https://regist.netkeiba.com/account/?pid=login&return_url={return_url}"
        
        driver.get(login_url)
        logger.info("ページロード完了。10秒待機...")
        time.sleep(10)
        
        # ログインIDを入力
        logger.info("ログインID入力中...")
        login_input = driver.find_element(By.NAME, "login_id")
        login_input.clear()
        login_input.send_keys(username)
        time.sleep(2)
        
        # パスワードを入力
        logger.info("パスワード入力中...")
        password_input = driver.find_element(By.NAME, "pswd")
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(2)
        
        # ログインボタンをクリック
        logger.info("ログインボタンをクリック...")
        login_button = driver.find_element(By.CSS_SELECTOR, "input[type='image']")
        login_button.click()
        
        logger.info("ログイン処理中... 30秒待機します")
        logger.info("ブラウザを確認してください：")
        logger.info("- ログインに成功しましたか？")
        logger.info("- エラーメッセージは表示されていますか？")
        logger.info("- レース詳細ページに移動しましたか？")
        
        time.sleep(30)
        
        # 現在のURL
        current_url = driver.current_url
        logger.info(f"現在のURL: {current_url}")
        
        # ページソースの一部を確認
        page_source = driver.page_source
        if "エラー" in page_source:
            logger.error("ページにエラーメッセージがあります")
        if "馬場指数" in page_source:
            logger.success("馬場指数という文字が見つかりました")
        if "プレミアム登録" in page_source:
            logger.warning("プレミアム登録という文字が見つかりました（ログイン失敗の可能性）")
        
        logger.info("\nブラウザウィンドウは自動的に閉じます（30秒後）")
        time.sleep(30)
        
    except Exception as e:
        logger.exception(f"エラー: {e}")
    finally:
        driver.quit()
        logger.info("デバッグ完了")


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    debug_login()
