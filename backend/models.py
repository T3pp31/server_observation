"""
データベースモデル
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(15), unique=True, index=True)
    mac_address = Column(String(17))
    hostname = Column(String(255))
    vendor = Column(String(255))
    os_info = Column(String(255))
    status = Column(String(20))  # online, offline, unknown
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
class PortScan(Base):
    __tablename__ = "port_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    device_ip = Column(String(15), index=True)
    scan_time = Column(DateTime, default=datetime.utcnow)
    port = Column(Integer)
    service = Column(String(50))
    service_name = Column(String(100))
    is_open = Column(Boolean, default=False)
    
class HttpResponse(Base):
    __tablename__ = "http_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    device_ip = Column(String(15), index=True)
    url = Column(String(500))
    status_code = Column(Integer)
    headers = Column(Text)  # JSON文字列として保存
    body_preview = Column(Text)  # ボディの一部を保存
    scan_time = Column(DateTime, default=datetime.utcnow)