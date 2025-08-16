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
        
        print(f"ポートスキャンを開始: {ip_address}, ポート: {all_ports}")
        
        try:
            # 全ポートを一度にスキャン（効率化）
            port_range = ','.join(map(str, all_ports))
            
            # -Pn: ホストディスカバリーをスキップ（ホストが生きていると仮定）
            # -sT: TCPコネクトスキャン（権限不要）
            # -T4: アグレッシブなタイミング
            # --host-timeout: ホストあたりの最大時間
            scan_args = f"-Pn -sT -T4 --host-timeout {PORT_SCAN_CONFIG['scan_timeout']}s"
            
            print(f"nmapコマンド実行: nmap {scan_args} -p {port_range} {ip_address}")
            
            self.nm.scan(
                hosts=ip_address, 
                ports=port_range, 
                arguments=scan_args,
                timeout=PORT_SCAN_CONFIG["scan_timeout"] * 2
            )
            
            print(f"スキャン完了。検出されたホスト: {self.nm.all_hosts()}")
            
            if ip_address in self.nm.all_hosts():
                host_info = self.nm[ip_address]
                print(f"ホスト情報: {host_info}")
                
                if 'tcp' in host_info:
                    for port in all_ports:
                        if port in host_info['tcp']:
                            port_state = host_info['tcp'][port]['state']
                            print(f"ポート {port}: 状態={port_state}")
                            
                            if port_state == 'open':
                                service = 'https' if port in PORT_SCAN_CONFIG["https_ports"] else 'http'
                                service_name = host_info['tcp'][port].get('name', 'unknown')
                                
                                port_info = {
                                    'port': port,
                                    'service': service,
                                    'service_name': service_name,
                                    'is_open': True
                                }
                                port_results.append(port_info)
                                print(f"オープンポート発見: {port_info}")
                                
                                # HTTPレスポンスを取得
                                http_response = self._get_http_response(ip_address, port, service)
                                if http_response:
                                    http_responses.append(http_response)
                else:
                    print("TCPポート情報が見つかりませんでした")
            else:
                print(f"ホスト {ip_address} が応答しませんでした")
                
        except Exception as e:
            print(f"ポートスキャンエラー: {e}")
            import traceback
            traceback.print_exc()
                
        print(f"スキャン結果: {len(port_results)}個のオープンポート, {len(http_responses)}個のHTTPレスポンス")
        
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