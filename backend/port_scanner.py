"""
ポートスキャナーモジュール
"""
import nmap
import requests
import json
from typing import Dict, List, Optional
import sys
sys.path.append('..')
from config.config import PORT_SCAN_CONFIG

class PortScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        
    def scan_ports(self, ip_address: str) -> Dict:
        """
        指定IPアドレスのHTTP/HTTPSポートをスキャン
        """
        all_ports = PORT_SCAN_CONFIG["http_ports"] + PORT_SCAN_CONFIG["https_ports"]
        port_results = []
        http_responses = []
        
        # ポートスキャンを実行
        for port in all_ports:
            try:
                self.nm.scan(hosts=ip_address, ports=str(port), timeout=PORT_SCAN_CONFIG["scan_timeout"])
                
                if ip_address in self.nm.all_hosts():
                    port_state = self.nm[ip_address]['tcp'][port]['state']
                    
                    if port_state == 'open':
                        service = 'https' if port in PORT_SCAN_CONFIG["https_ports"] else 'http'
                        service_name = self.nm[ip_address]['tcp'][port].get('name', 'unknown')
                        
                        port_info = {
                            'port': port,
                            'service': service,
                            'service_name': service_name,
                            'is_open': True
                        }
                        port_results.append(port_info)
                        
                        # HTTPレスポンスを取得
                        http_response = self._get_http_response(ip_address, port, service)
                        if http_response:
                            http_responses.append(http_response)
                            
            except Exception as e:
                print(f"ポート{port}のスキャンエラー: {e}")
                
        return {
            'port_scans': port_results,
            'http_responses': http_responses
        }
        
    def _get_http_response(self, ip: str, port: int, service: str) -> Optional[Dict]:
        """
        HTTPレスポンスを取得
        """
        url = f"{service}://{ip}:{port}"
        
        try:
            response = requests.get(
                url, 
                timeout=5, 
                verify=False,  # HTTPS証明書検証を無効化
                allow_redirects=False
            )
            
            # レスポンスヘッダーを辞書に変換
            headers = dict(response.headers)
            
            # ボディの一部を取得（最初の1000文字）
            body_preview = response.text[:1000] if response.text else ""
            
            return {
                'url': url,
                'status_code': response.status_code,
                'headers': headers,
                'body_preview': body_preview
            }
            
        except Exception as e:
            print(f"HTTPリクエストエラー ({url}): {e}")
            return None