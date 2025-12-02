"""
HTMLの構造をデバッグするスクリプト
"""
import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.scraper.base import BaseScraper

def debug_predictor_list():
    """予想家一覧ページのHTMLを保存"""
    scraper = BaseScraper()
    scraper.login()
    
    url = "https://yoso.sp.netkeiba.com/yosoka_search/result.html?prev_page=detail_search&_yosomenu=1&syusai=jra&range=current_year"
    
    print(f"Fetching: {url}")
    soup = scraper.get_page(url)
    
    if soup:
        # HTMLをファイルに保存
        with open("debug_predictor_list.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("✅ HTML saved to: debug_predictor_list.html")
        
        # 主要な要素を探す
        print("\n=== Searching for elements ===")
        
        # リンクを探す
        links = soup.find_all('a', href=True)
        predictor_links = [link for link in links if 'profile.html?id=' in link.get('href', '')]
        print(f"Found {len(predictor_links)} predictor profile links")
        
        if predictor_links:
            print("\n=== First 3 predictor links ===")
            for i, link in enumerate(predictor_links[:3], 1):
                print(f"\n{i}. Link: {link.get('href')}")
                print(f"   Text: {link.get_text(strip=True)}")
                print(f"   Parent: {link.parent.name}")
                print(f"   Parent class: {link.parent.get('class')}")
    else:
        print("❌ Failed to fetch page")

def debug_prediction_list():
    """予想家の予想一覧ページのHTMLを保存"""
    scraper = BaseScraper()
    scraper.login()
    
    predictor_id = 284  # サンプル予想家ID
    url = f"https://yoso.sp.netkeiba.com/yosoka/jra/profile.html?id={predictor_id}"
    
    print(f"\nFetching: {url}")
    soup = scraper.get_page(url)
    
    if soup:
        # HTMLをファイルに保存
        with open("debug_prediction_list.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("✅ HTML saved to: debug_prediction_list.html")
        
        # 主要な要素を探す
        print("\n=== Searching for prediction elements ===")
        
        # リンクを探す
        links = soup.find_all('a', href=True)
        prediction_links = [link for link in links if 'yoso_detail' in link.get('href', '')]
        print(f"Found {len(prediction_links)} prediction detail links")
        
        if prediction_links:
            print("\n=== First 3 prediction links ===")
            for i, link in enumerate(prediction_links[:3], 1):
                print(f"\n{i}. Link: {link.get('href')}")
                print(f"   Text: {link.get_text(strip=True)}")
                print(f"   Parent: {link.parent.name}")
                print(f"   Parent class: {link.parent.get('class')}")
    else:
        print("❌ Failed to fetch page")

def debug_prediction_detail():
    """予想詳細ページのHTMLを保存"""
    scraper = BaseScraper()
    scraper.login()
    
    prediction_id = 5528852  # サンプル予想ID
    url = f"https://yoso.sp.netkeiba.com/?pid=yoso_detail&id={prediction_id}"
    
    print(f"\nFetching: {url}")
    soup = scraper.get_page(url)
    
    if soup:
        # HTMLをファイルに保存
        with open("debug_prediction_detail.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("✅ HTML saved to: debug_prediction_detail.html")
    else:
        print("❌ Failed to fetch page")

if __name__ == "__main__":
    print("=== Debugging netkeiba HTML structure ===\n")
    
    debug_predictor_list()
    debug_prediction_list()
    debug_prediction_detail()
    
    print("\n=== Debug complete ===")
    print("Please check the generated HTML files:")
    print("  - debug_predictor_list.html")
    print("  - debug_prediction_list.html")
    print("  - debug_prediction_detail.html")
