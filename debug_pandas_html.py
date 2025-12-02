"""
pandas.read_html()方式のデバッグ
実際のHTMLとDataFrame構造を確認
"""
import pandas as pd
import requests
import random
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
]

race_id = "202508040109"
url = f"https://db.netkeiba.com/race/{race_id}"

print(f"URL: {url}\n")

# User-Agent付きでリクエスト
headers = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Content-Length: {len(response.content)} bytes\n")

# pandas.read_html()でテーブル取得
tables = pd.read_html(response.content)
print(f"テーブル数: {len(tables)}\n")

# 各テーブルの情報を表示
for i, table in enumerate(tables):
    print(f"=== Table {i} ===")
    print(f"形状: {table.shape} (行数={table.shape[0]}, 列数={table.shape[1]})")
    print(f"列名: {list(table.columns)}")
    
    # 最初の3行を表示
    print("\n最初の3行:")
    print(table.head(3))
    print("\n" + "="*80 + "\n")

# BeautifulSoupでHTMLを解析
soup = BeautifulSoup(response.content, 'html.parser')

# RaceData01を探す
print("=== RaceData01 を探す ===")
race_data01 = soup.find('div', class_='RaceData01')
print(f"見つかった: {race_data01 is not None}")
if race_data01:
    print(f"内容: {race_data01.get_text(strip=True)[:200]}")
print()

# RaceData02を探す
print("=== RaceData02 を探す ===")
race_data02 = soup.find('div', class_='RaceData02')
print(f"見つかった: {race_data02 is not None}")
if race_data02:
    print(f"内容: {race_data02.get_text(strip=True)[:200]}")
print()

# RaceNameを探す
print("=== RaceName を探す ===")
race_name = soup.find('div', class_='RaceName')
print(f"見つかった: {race_name is not None}")
if race_name:
    print(f"内容: {race_name.get_text(strip=True)[:200]}")
print()

# レース情報を探す（別のクラス名の可能性）
print("=== その他のクラス名を探す ===")
for class_name in ['data_intro', 'race_data', 'racedata', 'main_box', 'race_place', 'race_num']:
    elem = soup.find(class_=class_name)
    if elem:
        print(f"✅ {class_name}: {elem.get_text(strip=True)[:100]}")
    else:
        print(f"❌ {class_name}: 見つからない")

print("\n=== 完了 ===")
