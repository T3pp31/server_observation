"""
FastAPIアプリケーション
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime

import sys
sys.path.append('..')

from backend.database import get_db, init_db
from backend import models, schemas
from backend.network_scanner import NetworkScanner
from backend.port_scanner import PortScanner
from config.config import API_CONFIG

# FastAPIインスタンスの作成
app = FastAPI(title="LAN監視 API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 起動時の処理
@app.on_event("startup")
def startup_event():
    init_db()

# スキャナーインスタンス
network_scanner = NetworkScanner()
port_scanner = PortScanner()

@app.get("/")
def read_root():
    return {"message": "LAN監視 API"}

@app.get("/api/devices", response_model=List[schemas.Device])
def get_devices(db: Session = Depends(get_db)):
    """
    全デバイスの一覧を取得
    """
    devices = db.query(models.Device).all()
    return devices

@app.get("/api/devices/{ip_address}", response_model=schemas.DeviceDetail)
def get_device_detail(ip_address: str, db: Session = Depends(get_db)):
    """
    特定デバイスの詳細情報を取得
    """
    device = db.query(models.Device).filter(models.Device.ip_address == ip_address).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # ポートスキャン結果を取得
    port_scans = db.query(models.PortScan).filter(
        models.PortScan.device_ip == ip_address
    ).order_by(models.PortScan.scan_time.desc()).limit(10).all()
    
    # HTTPレスポンス情報を取得
    http_responses = db.query(models.HttpResponse).filter(
        models.HttpResponse.device_ip == ip_address
    ).order_by(models.HttpResponse.scan_time.desc()).limit(5).all()
    
    # ヘッダー情報をJSONからdictに変換
    for response in http_responses:
        if response.headers:
            response.headers = json.loads(response.headers)
    
    device_detail = schemas.DeviceDetail(
        **device.__dict__,
        port_scans=port_scans,
        http_responses=http_responses
    )
    
    return device_detail

@app.post("/api/scan/network")
def scan_network(scan_request: schemas.ScanRequest, db: Session = Depends(get_db)):
    """
    ネットワークスキャンを実行
    """
    devices = network_scanner.scan_network(scan_request.network_range)
    
    # スキャン結果を保存
    for device_data in devices:
        # 既存のデバイスかチェック
        existing_device = db.query(models.Device).filter(
            models.Device.ip_address == device_data['ip_address']
        ).first()
        
        if existing_device:
            # 更新
            for key, value in device_data.items():
                if value is not None:
                    setattr(existing_device, key, value)
            existing_device.last_seen = datetime.utcnow()
        else:
            # 新規作成
            new_device = models.Device(**device_data)
            db.add(new_device)
    
    db.commit()
    
    return {
        "message": "Network scan completed",
        "devices_found": len(devices)
    }

@app.delete("/api/devices/reset")
def reset_devices(db: Session = Depends(get_db)):
    """
    全デバイス情報をリセット（削除）
    """
    try:
        # 全デバイスを削除
        deleted_count = db.query(models.Device).count()
        db.query(models.Device).delete()
        db.commit()
        
        return {
            "message": "All devices have been reset",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reset devices: {str(e)}")

@app.post("/api/scan/ports")
def scan_ports(scan_request: schemas.ScanRequest, db: Session = Depends(get_db)):
    """
    ポートスキャンを実行
    """
    if not scan_request.ip_address:
        raise HTTPException(status_code=400, detail="IP address is required")
    
    # デバイスの存在確認
    device = db.query(models.Device).filter(
        models.Device.ip_address == scan_request.ip_address
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # ポートスキャン実行
    scan_results = port_scanner.scan_ports(scan_request.ip_address)
    
    # ポートスキャン結果を保存
    for port_info in scan_results['port_scans']:
        port_scan = models.PortScan(
            device_ip=scan_request.ip_address,
            **port_info
        )
        db.add(port_scan)
    
    # HTTPレスポンス情報を保存
    for http_info in scan_results['http_responses']:
        # ヘッダーをJSON文字列に変換
        headers_json = json.dumps(http_info['headers']) if http_info['headers'] else None
        
        http_response = models.HttpResponse(
            device_ip=scan_request.ip_address,
            url=http_info['url'],
            status_code=http_info['status_code'],
            headers=headers_json,
            body_preview=http_info['body_preview']
        )
        db.add(http_response)
    
    db.commit()
    
    return {
        "message": "Port scan completed",
        "open_ports": len(scan_results['port_scans']),
        "http_responses": len(scan_results['http_responses'])
    }

@app.put("/api/devices/{ip_address}")
def update_device(
    ip_address: str, 
    device_update: schemas.DeviceUpdate, 
    db: Session = Depends(get_db)
):
    """
    デバイス情報の更新
    """
    device = db.query(models.Device).filter(
        models.Device.ip_address == ip_address
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    for key, value in device_update.dict(exclude_unset=True).items():
        setattr(device, key, value)
    
    device.last_seen = datetime.utcnow()
    db.commit()
    
    return {"message": "Device updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=API_CONFIG["host"], 
        port=API_CONFIG["port"], 
        reload=API_CONFIG["reload"]
    )