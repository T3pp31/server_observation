"""
Çü¿Ùü¹¥šh»Ã·çó¡
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys
sys.path.append('..')
from config.config import DATABASE_URL
from backend.models import Base

# Çü¿Ùü¹¨ó¸ón\
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# »Ã·çóíü«ë¯é¹n\
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Çü¿Ùü¹nX'
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ÆüÖën\
def init_db():
    Base.metadata.create_all(bind=engine)