"""
データベース接続設定
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.config import settings
from backend.models.database import Base
import os


# データベースディレクトリの作成
os.makedirs("data", exist_ok=True)

# エンジンの作成
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """データベースを初期化"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def drop_db():
    """データベースを削除（テスト用）"""
    Base.metadata.drop_all(bind=engine)
    print("Database dropped!")
