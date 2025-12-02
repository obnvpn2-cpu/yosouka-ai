"""
デバッグ用：netkeiba.comのHTML構造を確認
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# ChromeDriverのパス
driver_path = "drivers/chromedriver.exe"

# ドライバー起動
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # デバッグのためheadlessを無効化
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# レースページを開く
race_id = "202508040109"
url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}"

print(f"URL: {url}")
driver.get(url)
time.sleep(3)

# RaceData01の内容を確認
try:
    race_data01 = driver.find_element(By.CLASS_NAME, "RaceData01")
    print("\n=== RaceData01 の内容 ===")
    print(race_data01.text)
    print(f"\nHTML: {race_data01.get_attribute('innerHTML')[:500]}")
except Exception as e:
    print(f"RaceData01取得エラー: {e}")

# RaceData02の内容を確認
try:
    race_data02 = driver.find_element(By.CLASS_NAME, "RaceData02")
    print("\n=== RaceData02 の内容 ===")
    print(race_data02.text)
    print(f"\nHTML: {race_data02.get_attribute('innerHTML')[:500]}")
except Exception as e:
    print(f"RaceData02取得エラー: {e}")

# RaceNameの内容を確認
try:
    race_name = driver.find_element(By.CLASS_NAME, "RaceName")
    print("\n=== RaceName の内容 ===")
    print(race_name.text)
    print(f"\nHTML: {race_name.get_attribute('innerHTML')[:500]}")
except Exception as e:
    print(f"RaceName取得エラー: {e}")

# ページ全体のタイトル部分を確認
try:
    title_elem = driver.find_element(By.TAG_NAME, "title")
    print(f"\n=== Page Title ===")
    print(title_elem.get_attribute('text'))
except Exception as e:
    print(f"Title取得エラー: {e}")

# 5秒待機（手動確認用）
print("\n5秒後にブラウザを閉じます...")
time.sleep(5)

driver.quit()
print("完了")
