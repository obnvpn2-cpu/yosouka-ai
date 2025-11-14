"""
データベース初期化スクリプト
"""
from backend.database import init_db, drop_db
import sys


def main():
    """データベースを初期化"""
    print("Initializing database...")
    
    # 既存のデータベースを削除するか確認
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        response = input("Are you sure you want to drop the existing database? (yes/no): ")
        if response.lower() == "yes":
            print("Dropping existing database...")
            drop_db()
    
    # データベースを作成
    init_db()
    print("Database initialization complete!")
    print("\nNext steps:")
    print("1. Update .env file with your netkeiba credentials")
    print("2. Run: python -m backend.scraper.main")


if __name__ == "__main__":
    main()
