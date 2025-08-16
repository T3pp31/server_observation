"""
設定ファイル
"""
import os
from pathlib import Path

# プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# データベース設定
DATABASE_URL = f"sqlite:///{BASE_DIR}/database/lan_monitor.db"

# ネットワークスキャン設定
NETWORK_SCAN_CONFIG = {
    "default_network": "192.168.1.0/24",  # デフォルトのスキャン範囲
    "scan_timeout": 10,  # スキャンタイムアウト（秒）
    "ping_timeout": 1,  # ping応答タイムアウト（秒）
}

# ポートスキャン設定
PORT_SCAN_CONFIG = {
    "http_ports": [80, 8080, 8000, 3000],
    "https_ports": [443, 8443],
    "scan_timeout": 15,  # ポートスキャンタイムアウト（秒）
}

# API設定
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "cors_origins": [
        "http://localhost:3000",
        "http://10.10.15.212:3000",
        "http://127.0.0.1:3000",
        "*"  # 開発環境では全てのオリジンを許可
    ],
}

# セキュリティ設定
SECURITY_CONFIG = {
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key-here"),
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
}