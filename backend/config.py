"""
アプリケーション設定
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # Database
    database_url: str = "sqlite:///./data/keiba.db"
    
    # netkeiba Credentials
    netkeiba_username: Optional[str] = None
    netkeiba_password: Optional[str] = None
    
    # Scraping Settings
    scraping_delay: int = 3  # リクエスト間隔（秒）
    max_retries: int = 3     # 最大リトライ回数
    request_timeout: int = 30  # タイムアウト（秒）
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# グローバル設定インスタンス
settings = Settings()
