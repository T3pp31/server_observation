"""
データベース接続設定
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys
sys.path.append('..')
from config.config import DATABASE_URL
from backend.models import Base

# エンジンの作成
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# セッション取得関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# テーブル作成
def init_db():
    Base.metadata.create_all(bind=engine)