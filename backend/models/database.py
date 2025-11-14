"""
データベースモデル
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Predictor(Base):
    """予想家テーブル"""
    __tablename__ = "predictors"
    
    id = Column(Integer, primary_key=True, index=True)
    netkeiba_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    profile = Column(Text, nullable=True)
    total_predictions = Column(Integer, default=0)
    grade_race_predictions = Column(Integer, default=0)
    data_reliability = Column(String(20), default="low")  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    predictions = relationship("Prediction", back_populates="predictor", cascade="all, delete-orphan")
    stats = relationship("PredictorStats", back_populates="predictor", cascade="all, delete-orphan")


class Race(Base):
    """レーステーブル"""
    __tablename__ = "races"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String(20), unique=True, index=True, nullable=False)  # netkeibaのレースID
    race_name = Column(String(200), nullable=False)
    race_date = Column(DateTime, nullable=False, index=True)
    venue = Column(String(50), nullable=False)  # 競馬場
    grade = Column(String(20), nullable=True)  # G1, G2, G3, OP, 3勝, 2勝, 1勝, 未勝利, 新馬
    distance = Column(Integer, nullable=False)
    track_type = Column(String(20), nullable=False)  # 芝, ダート
    track_condition = Column(String(20), nullable=True)  # 良, 稍重, 重, 不良
    horse_count = Column(Integer, nullable=True)
    is_grade_race = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    predictions = relationship("Prediction", back_populates="race", cascade="all, delete-orphan")
    result = relationship("RaceResult", back_populates="race", uselist=False, cascade="all, delete-orphan")


class Prediction(Base):
    """予想テーブル"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    predictor_id = Column(Integer, ForeignKey("predictors.id"), nullable=False, index=True)
    race_id = Column(Integer, ForeignKey("races.id"), nullable=False, index=True)
    netkeiba_prediction_id = Column(Integer, unique=True, index=True)  # netkeibaの予想ID
    predicted_at = Column(DateTime, nullable=False)
    
    # 予想内容
    favorite_horse = Column(Integer, nullable=True)  # 本命馬番
    rival_horse = Column(Integer, nullable=True)     # 対抗馬番
    dark_horse = Column(Integer, nullable=True)      # 単穴馬番
    bet_type = Column(String(20), nullable=True)     # 馬券種
    bet_horses = Column(String(100), nullable=True)  # 買い目
    comment = Column(Text, nullable=True)            # 見解
    
    # 結果
    is_hit = Column(Boolean, nullable=True)          # 的中/不的中
    payout = Column(Integer, nullable=True)          # 払戻金
    roi = Column(Float, nullable=True)               # 回収率
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    predictor = relationship("Predictor", back_populates="predictions")
    race = relationship("Race", back_populates="predictions")


class RaceResult(Base):
    """レース結果テーブル"""
    __tablename__ = "race_results"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.id"), nullable=False, unique=True)
    
    # 着順（JSON文字列として保存）
    finishing_order = Column(Text, nullable=True)
    
    # 払戻金
    win_payout = Column(Integer, nullable=True)         # 単勝
    place_payout = Column(String(100), nullable=True)   # 複勝（複数の場合カンマ区切り）
    exacta_payout = Column(Integer, nullable=True)      # 馬連
    quinella_payout = Column(Integer, nullable=True)    # 馬単
    wide_payout = Column(String(100), nullable=True)    # ワイド
    trio_payout = Column(Integer, nullable=True)        # 3連複
    trifecta_payout = Column(Integer, nullable=True)    # 3連単
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    race = relationship("Race", back_populates="result")


class PredictorStats(Base):
    """予想家統計テーブル"""
    __tablename__ = "predictor_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    predictor_id = Column(Integer, ForeignKey("predictors.id"), nullable=False, index=True)
    
    stat_type = Column(String(50), nullable=False)  # overall, grade_race, venue, distance等
    condition = Column(String(100), nullable=True)  # 条件（例: "tokyo_turf_g1"）
    
    sample_size = Column(Integer, default=0)        # サンプル数
    hit_rate = Column(Float, default=0.0)           # 的中率
    roi = Column(Float, default=0.0)                # 回収率
    confidence_level = Column(String(20), nullable=True)  # 信頼度
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    predictor = relationship("Predictor", back_populates="stats")
