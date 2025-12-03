#!/usr/bin/env python3
"""
Phase 4.3: FastAPI実装
条件指定検索機能をWeb APIとして提供
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3
import pandas as pd
from pathlib import Path
import sys

# 最小予想数（固定値）
MIN_PREDICTIONS = 5

# FastAPIアプリケーション
app = FastAPI(
    title="競馬予想家分析API",
    description="条件指定による予想家検索API",
    version="1.0.0"
)

# CORS設定（フロントエンドから呼び出せるように）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# リクエスト/レスポンスモデル
# ========================================

class SearchRequest(BaseModel):
    """検索リクエスト"""
    venue: Optional[str] = Field(None, description="競馬場（例: 東京, 京都, 中山）")
    track_type: Optional[str] = Field(None, description="コース種別（芝, ダート）")
    distances: Optional[List[int]] = Field(None, description="距離のリスト（例: [1600, 2000]）")
    grade: Optional[str] = Field(None, description="グレード（G1, G2, G3, オープン, 一般）")
    sort_by: str = Field("hit_rate", description="ソート基準（hit_rate, roi）")
    limit: int = Field(50, description="取得件数")

class PredictorResult(BaseModel):
    """予想家の検索結果"""
    predictor_id: int
    predictor_name: str
    netkeiba_id: int
    prediction_count: int
    hit_count: int
    hit_rate: float
    total_payout: int
    avg_payout: float
    roi_count: int
    avg_roi: Optional[float]

class SearchResponse(BaseModel):
    """検索レスポンス"""
    total_count: int = Field(..., description="該当予想家数")
    avg_hit_rate: float = Field(..., description="平均的中率")
    max_hit_rate: float = Field(..., description="最高的中率")
    total_predictions: int = Field(..., description="総予想数")
    predictors: List[PredictorResult] = Field(..., description="予想家リスト")

class OptionsResponse(BaseModel):
    """検索条件の選択肢"""
    venues: List[str] = Field(..., description="競馬場リスト")
    track_types: List[str] = Field(..., description="コース種別リスト")
    distances: List[int] = Field(..., description="距離リスト")
    grades: List[str] = Field(..., description="グレードリスト")
    min_predictions: int = Field(..., description="最小予想数")

# ========================================
# ヘルパー関数
# ========================================

def get_db_connection():
    """データベース接続を取得"""
    db_path = Path('data/keiba.db')
    
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="データベースが見つかりません")
    
    return sqlite3.connect(db_path)

def search_predictors_internal(
    venue: Optional[str],
    track_type: Optional[str],
    distances: Optional[List[int]],
    grade: Optional[str],
    sort_by: str,
    limit: int
) -> pd.DataFrame:
    """
    内部用の検索関数
    """
    
    conn = get_db_connection()
    
    # WHERE句を構築
    where_clauses = []
    params = []
    
    if venue:
        where_clauses.append("r.venue = ?")
        params.append(venue)
    
    if track_type:
        where_clauses.append("r.track_type = ?")
        params.append(track_type)
    
    if distances:
        distance_placeholders = ','.join(['?'] * len(distances))
        where_clauses.append(f"r.distance IN ({distance_placeholders})")
        params.extend(distances)
    
    if grade:
        if grade in ['G1', 'G2', 'G3']:
            where_clauses.append("r.grade = ?")
            params.append(grade)
        elif grade == 'オープン':
            where_clauses.append("r.is_grade_race = 1")
        elif grade == '一般':
            where_clauses.append("(r.is_grade_race = 0 OR r.is_grade_race IS NULL)")
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # ソート基準
    order_by = "hit_rate DESC" if sort_by == 'hit_rate' else "avg_roi DESC"
    
    # クエリ実行
    query = f"""
    SELECT 
        pred.id as predictor_id,
        pred.name as predictor_name,
        pred.netkeiba_id,
        COUNT(*) as prediction_count,
        SUM(CASE WHEN p.is_hit = 1 THEN 1 ELSE 0 END) as hit_count,
        ROUND(AVG(CASE WHEN p.is_hit = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as hit_rate,
        SUM(CASE WHEN p.payout IS NOT NULL THEN p.payout ELSE 0 END) as total_payout,
        ROUND(AVG(CASE WHEN p.payout IS NOT NULL THEN p.payout ELSE 0 END), 0) as avg_payout,
        COUNT(CASE WHEN p.roi IS NOT NULL THEN 1 END) as roi_count,
        ROUND(AVG(CASE WHEN p.roi IS NOT NULL THEN p.roi ELSE NULL END), 2) as avg_roi
    FROM predictors pred
    JOIN predictions p ON pred.id = p.predictor_id
    JOIN races r ON p.race_id = r.id
    WHERE {where_sql}
      AND p.is_hit IS NOT NULL
    GROUP BY pred.id
    HAVING prediction_count >= ?
    ORDER BY {order_by}
    LIMIT ?
    """
    
    params.extend([MIN_PREDICTIONS, limit])
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

# ========================================
# エンドポイント
# ========================================

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {
        "status": "ok",
        "service": "競馬予想家分析API",
        "version": "1.0.0"
    }

@app.get("/api/options", response_model=OptionsResponse)
async def get_options():
    """
    検索条件の選択肢を取得
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 競馬場
        cursor.execute("""
            SELECT DISTINCT venue 
            FROM races 
            WHERE venue IS NOT NULL AND venue != '不明'
            ORDER BY venue
        """)
        venues = [row[0] for row in cursor.fetchall()]
        
        # コース種別
        cursor.execute("""
            SELECT DISTINCT track_type 
            FROM races 
            WHERE track_type IS NOT NULL AND track_type != '不明'
            ORDER BY track_type
        """)
        track_types = [row[0] for row in cursor.fetchall()]
        
        # 距離
        cursor.execute("""
            SELECT DISTINCT distance 
            FROM races 
            WHERE distance IS NOT NULL AND distance > 0
            ORDER BY distance
        """)
        distances = [row[0] for row in cursor.fetchall()]
        
        # グレード
        grades = ['G1', 'G2', 'G3', 'オープン', '一般']
        
        conn.close()
        
        return OptionsResponse(
            venues=venues,
            track_types=track_types,
            distances=distances,
            grades=grades,
            min_predictions=MIN_PREDICTIONS
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=SearchResponse)
async def search_predictors(request: SearchRequest):
    """
    条件指定による予想家検索
    """
    
    try:
        # 検索実行
        df = search_predictors_internal(
            venue=request.venue,
            track_type=request.track_type,
            distances=request.distances,
            grade=request.grade,
            sort_by=request.sort_by,
            limit=request.limit
        )
        
        # 結果が空の場合
        if len(df) == 0:
            return SearchResponse(
                total_count=0,
                avg_hit_rate=0.0,
                max_hit_rate=0.0,
                total_predictions=0,
                predictors=[]
            )
        
        # DataFrameをPydanticモデルに変換
        predictors = []
        for _, row in df.iterrows():
            predictors.append(PredictorResult(
                predictor_id=int(row['predictor_id']),
                predictor_name=row['predictor_name'],
                netkeiba_id=int(row['netkeiba_id']),
                prediction_count=int(row['prediction_count']),
                hit_count=int(row['hit_count']),
                hit_rate=float(row['hit_rate']),
                total_payout=int(row['total_payout']),
                avg_payout=float(row['avg_payout']),
                roi_count=int(row['roi_count']),
                avg_roi=float(row['avg_roi']) if pd.notna(row['avg_roi']) else None
            ))
        
        return SearchResponse(
            total_count=len(df),
            avg_hit_rate=float(df['hit_rate'].mean()),
            max_hit_rate=float(df['hit_rate'].max()),
            total_predictions=int(df['prediction_count'].sum()),
            predictors=predictors
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """
    全体統計を取得
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 基本統計
        cursor.execute("SELECT COUNT(*) FROM predictors")
        total_predictors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total_predictions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM races")
        total_races = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM races 
            WHERE track_type IS NOT NULL AND track_type != '不明'
        """)
        races_with_detail = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_predictors": total_predictors,
            "total_predictions": total_predictions,
            "total_races": total_races,
            "races_with_detail": races_with_detail,
            "min_predictions": MIN_PREDICTIONS
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 起動用
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
