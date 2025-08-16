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
        指定IPアドレスの全ポート（1-65535）をスキャン
        """
        port_results = []
        http_responses = []
        
        print(f"全ポートスキャンを開始: {ip_address}, ポート範囲: {PORT_SCAN_CONFIG['port_range']}")
        
        try:
            # -Pn: ホストディスカバリーをスキップ（ホストが生きていると仮定）
            # -sS: SYNスキャン（高速）、権限がない場合は自動的に-sTに切り替わる
            # -T3: 通常タイミング（ネットワークに優しい）
            # --max-retries: 再試行回数制限
            # --host-timeout: ホストあたりの最大時間
            scan_args = f"-Pn -sS -{PORT_SCAN_CONFIG['timing_template']} --max-retries {PORT_SCAN_CONFIG['max_retries']} --host-timeout {PORT_SCAN_CONFIG['scan_timeout']}s"
            
            print(f"nmapコマンド実行: nmap {scan_args} -p {PORT_SCAN_CONFIG['port_range']} {ip_address}")
            
            self.nm.scan(
                hosts=ip_address, 
                ports=PORT_SCAN_CONFIG['port_range'], 
                arguments=scan_args,
                timeout=PORT_SCAN_CONFIG["scan_timeout"]
            )
            
            print(f"スキャン完了。検出されたホスト: {self.nm.all_hosts()}")
            
            if ip_address in self.nm.all_hosts():
                host_info = self.nm[ip_address]
                print(f"ホスト状態: {host_info.get('status', {}).get('state', 'unknown')}")
                
                if 'tcp' in host_info:
                    tcp_ports = host_info['tcp']
                    print(f"TCPポート情報: {len(tcp_ports)}個のポートをスキャン")
                    
                    for port, port_info in tcp_ports.items():
                        port_state = port_info['state']
                        
                        if port_state == 'open':
                            service_name = port_info.get('name', 'unknown')
                            service_product = port_info.get('product', '')
                            service_version = port_info.get('version', '')
                            
                            # サービス情報の構築
                            service_detail = service_name
                            if service_product:
                                service_detail += f" ({service_product}"
                                if service_version:
                                    service_detail += f" {service_version}"
                                service_detail += ")"
                            
                            # HTTPまたはHTTPSサービスの判定
                            is_http_service = self._is_http_service(port, service_name)
                            service_type = self._determine_service_type(port, service_name)
                            
                            port_result = {
                                'port': port,
                                'service': service_type,
                                'service_name': service_detail,
                                'is_open': True
                            }
                            port_results.append(port_result)
                            print(f"オープンポート発見: ポート{port} - {service_detail}")
                            
                            # HTTPサービスの場合はレスポンスを取得
                            if is_http_service:
                                http_response = self._get_http_response(ip_address, port, service_type)
                                if http_response:
                                    http_responses.append(http_response)
                    
                    print(f"オープンポート総数: {len(port_results)}個")
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
    
    def _is_http_service(self, port: int, service_name: str) -> bool:
        """
        HTTPサービスかどうかを判定
        """
        http_ports = [80, 8080, 8000, 8888, 3000, 5000, 9000]
        https_ports = [443, 8443, 9443]
        http_services = ['http', 'https', 'http-proxy', 'http-alt', 'webcache']
        
        return (port in http_ports + https_ports or 
                any(http_service in service_name.lower() for http_service in http_services))
    
    def _determine_service_type(self, port: int, service_name: str) -> str:
        """
        サービスタイプを判定（HTTP/HTTPS/その他）
        """
        https_ports = [443, 8443, 9443]
        https_services = ['https', 'ssl', 'tls']
        
        if port in https_ports or any(https_service in service_name.lower() for https_service in https_services):
            return 'https'
        elif self._is_http_service(port, service_name):
            return 'http'
        else:
            return 'other'
        
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