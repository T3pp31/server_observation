"""
Pydantic¹­üÞš©
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class DeviceBase(BaseModel):
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    os_info: Optional[str] = None
    status: str = "unknown"

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    os_info: Optional[str] = None
    status: Optional[str] = None

class Device(DeviceBase):
    id: int
    first_detected: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True

class PortScanBase(BaseModel):
    device_ip: str
    port: int
    service: Optional[str] = None
    service_name: Optional[str] = None
    is_open: bool = False

class PortScan(PortScanBase):
    id: int
    scan_time: datetime
    
    class Config:
        from_attributes = True

class HttpResponseBase(BaseModel):
    device_ip: str
    url: str
    status_code: Optional[int] = None
    headers: Optional[Dict] = None
    body_preview: Optional[str] = None

class HttpResponse(HttpResponseBase):
    id: int
    scan_time: datetime
    
    class Config:
        from_attributes = True

class DeviceDetail(Device):
    port_scans: List[PortScan] = []
    http_responses: List[HttpResponse] = []

class ScanRequest(BaseModel):
    network_range: Optional[str] = None
    ip_address: Optional[str] = None