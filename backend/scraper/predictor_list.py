"""
予想家一覧を取得するスクレイパー
"""
from typing import List, Dict
from backend.scraper.base import BaseScraper
from loguru import logger


class PredictorListScraper(BaseScraper):
    """予想家一覧を取得するスクレイパー"""
    
    def get_predictor_list(self, year_range: str = "current_year") -> List[Dict]:
        """
        予想家一覧を取得
        
        Args:
            year_range: 年範囲（current_year, prev1_year, prev2_year）
        
        Returns:
            予想家情報のリスト
        """
        url = f"https://yoso.sp.netkeiba.com/yosoka_search/result.html?prev_page=detail_search&_yosomenu=1&syusai=jra&range={year_range}"
        
        soup = self.get_page(url)
        if not soup:
            logger.error("Failed to fetch predictor list")
            return []
        
        predictors = []
        
        try:
            # 予想家のリストを含む要素を探す
            # 実際のHTML構造: <ul class="YosokaResultList Yosoka"> の中に <li> タグ
            
            predictor_elements = soup.select('ul.YosokaResultList li')
            
            if not predictor_elements:
                logger.warning("No predictor elements found. HTML structure may have changed.")
                logger.debug(f"Page title: {soup.title.string if soup.title else 'No title'}")
                return []
            
            for element in predictor_elements:
                try:
                    # 予想家IDを <li> の id 属性から抽出（例: id="yosoka_s_206"）
                    li_id = element.get('id', '')
                    if not li_id.startswith('yosoka_s_'):
                        continue
                    
                    predictor_id = int(li_id.replace('yosoka_s_', ''))
                    
                    # 予想家名を抽出（<div class="YosokaName">）
                    name_element = element.find('div', class_='YosokaName')
                    if not name_element:
                        continue
                    
                    name = self.extract_text(name_element)
                    if not name:
                        continue
                    
                    # 回収率を抽出
                    roi = None
                    roi_dd = None
                    dts = element.find_all('dt')
                    for dt in dts:
                        if '回収率' in self.extract_text(dt):
                            # 次の dd 要素を取得
                            dd = dt.find_next_sibling('dd')
                            if dd:
                                roi_text = self.extract_text(dd)
                                roi = self.extract_float(roi_text)
                            break
                    
                    # 的中率を抽出
                    hit_rate = None
                    for dt in dts:
                        if '的中率' in self.extract_text(dt):
                            dd = dt.find_next_sibling('dd')
                            if dd:
                                hit_rate_text = self.extract_text(dd)
                                hit_rate = self.extract_float(hit_rate_text)
                            break
                    
                    # 予想数を抽出
                    prediction_count = None
                    for dt in dts:
                        if '予想数' in self.extract_text(dt):
                            dd = dt.find_next_sibling('dd')
                            if dd:
                                count_text = self.extract_text(dd)
                                prediction_count = self.extract_int(count_text)
                            break
                    
                    predictor_info = {
                        'netkeiba_id': predictor_id,
                        'name': name,
                        'hit_rate': hit_rate,
                        'roi': roi,
                        'prediction_count': prediction_count
                    }
                    
                    predictors.append(predictor_info)
                    logger.debug(f"Found predictor: {name} (ID: {predictor_id}, 回収率: {roi}%, 的中率: {hit_rate}%)")
                    
                except Exception as e:
                    logger.warning(f"Error parsing predictor element: {e}")
                    continue
            
            logger.info(f"Found {len(predictors)} predictors for {year_range}")
            return predictors
            
        except Exception as e:
            logger.error(f"Error extracting predictor list: {e}")
            return []
    
    def get_all_active_predictors(self) -> List[Dict]:
        """
        過去3年間にアクティブな予想家をすべて取得
        
        Returns:
            予想家情報のリスト（重複除去済み）
        """
        all_predictors = {}
        
        for year_range in ["current_year", "prev1_year", "prev2_year"]:
            logger.info(f"Fetching predictors for {year_range}")
            predictors = self.get_predictor_list(year_range)
            
            # 重複を除去（IDをキーにして最新情報を保持）
            for predictor in predictors:
                predictor_id = predictor['netkeiba_id']
                if predictor_id not in all_predictors:
                    all_predictors[predictor_id] = predictor
        
        result = list(all_predictors.values())
        logger.info(f"Total unique predictors: {len(result)}")
        return result