"""
��������h�÷��
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys
sys.path.append('..')
from config.config import DATABASE_URL
from backend.models import Base

# ���������n\
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# �÷�������n\
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ������n�X'
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ����n\
def init_db():
    Base.metadata.create_all(bind=engine)