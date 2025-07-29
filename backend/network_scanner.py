"""
ネットワークスキャナーモジュール
"""
import nmap
import socket
import subprocess
import re
from typing import Dict, List, Optional
import sys
sys.path.append('..')
from config.config import NETWORK_SCAN_CONFIG

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        
    def scan_network(self, network_range: str = None) -> List[Dict]:
        """
        ネットワーク内のデバイスをスキャン
        """
        if not network_range:
            network_range = NETWORK_SCAN_CONFIG["default_network"]
            
        devices = []
        
        try:
            print(f"スキャン開始: {network_range}")
            
            # pingスキャンを実行
            self.nm.scan(hosts=network_range, arguments='-sn')
            
            # スキャン結果を処理
            for host in self.nm.all_hosts():
                print(f"ホスト発見: {host}")
                device_info = {
                    'ip_address': host,
                    'status': 'online' if self.nm[host].state() == 'up' else 'offline',
                    'hostname': self._get_hostname(host),
                    'mac_address': self._get_mac_address(host),
                    'vendor': self._get_vendor(host)
                }
                
                # OS情報の取得を試みる（オプション）
                # 注：OS検出には root 権限が必要で、時間がかかるため、デフォルトでは無効
                # os_info = self._get_os_info(host)
                # if os_info:
                #     device_info['os_info'] = os_info
                    
                devices.append(device_info)
            
            # スキャン結果が空の場合、単一IPとして処理
            if not devices and '/' not in network_range:
                print(f"単一IPアドレスとして処理: {network_range}")
                # 単一IPアドレスの場合は直接チェック
                device_info = {
                    'ip_address': network_range,
                    'status': 'unknown',  # pingスキャンが失敗した場合は不明とする
                    'hostname': self._get_hostname(network_range),
                    'mac_address': self._get_mac_address(network_range),
                    'vendor': None
                }
                
                # 接続可能性をチェック
                try:
                    socket.setdefaulttimeout(2)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex((network_range, 80))  # ポート80で接続テスト
                    sock.close()
                    if result == 0:
                        device_info['status'] = 'online'
                except:
                    pass
                    
                devices.append(device_info)
                
        except Exception as e:
            print(f"ネットワークスキャンエラー: {e}")
            raise e  # エラーを上位に伝播
            
        print(f"スキャン完了: {len(devices)}台のデバイスを発見")
        return devices
    
    def _get_hostname(self, ip: str) -> Optional[str]:
        """
        IPアドレスからホスト名を取得
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except:
            return None
            
    def _get_mac_address(self, ip: str) -> Optional[str]:
        """
        MACアドレスを取得（ARPテーブルから）
        """
        try:
            # Linux用のarpコマンドを実行
            result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
            if result.returncode == 0:
                # MACアドレスを抽出
                match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', result.stdout)
                if match:
                    return match.group(0)
        except:
            pass
        return None
        
    def _get_vendor(self, ip: str) -> Optional[str]:
        """
        MACアドレスからベンダー情報を取得
        """
        try:
            if ip in self.nm.all_hosts() and 'vendor' in self.nm[ip]:
                vendors = self.nm[ip]['vendor']
                if vendors:
                    return list(vendors.values())[0]
        except:
            pass
        return None
        
    def _get_os_info(self, ip: str) -> Optional[str]:
        """
        OS情報を推測
        """
        try:
            # OSスキャン（要root権限）
            self.nm.scan(hosts=ip, arguments='-O')
            if 'osmatch' in self.nm[ip]:
                os_matches = self.nm[ip]['osmatch']
                if os_matches:
                    return os_matches[0]['name']
        except:
            pass
        return None