"""
ネットワークスキャナーモジュール
"""
import nmap
import socket
import subprocess
import re
import concurrent.futures
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
            
            # Docker環境かどうかの判定
            is_docker = self._is_running_in_docker()
            print(f"Docker環境での実行: {is_docker}")
            
            if is_docker:
                # Docker環境の場合は、より制限的なスキャンを行う
                devices = self._scan_with_ping_validation(network_range)
            else:
                # 通常環境での nmap スキャン
                self.nm.scan(hosts=network_range, arguments='-sn -R')
                active_hosts = self.nm.all_hosts()
                print(f"応答したホスト数: {len(active_hosts)}")
                
                for host in active_hosts:
                    host_state = self.nm[host].state()
                    print(f"ホスト発見: {host} (状態: {host_state})")
                    
                    if host_state == 'up':
                        device_info = {
                            'ip_address': host,
                            'status': 'online',
                            'hostname': self._get_hostname(host),
                            'mac_address': self._get_mac_address(host),
                            'vendor': self._get_vendor(host)
                        }
                        devices.append(device_info)
                    else:
                        print(f"ホスト {host} は非アクティブ状態: {host_state}")
            
            # スキャン結果が空の場合、単一IPアドレスのみ処理
            if not devices and '/' not in network_range and '-' not in network_range:
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
        # Method 1: socket.gethostbyaddr
        try:
            socket.setdefaulttimeout(3)
            hostname, _, _ = socket.gethostbyaddr(ip)
            if hostname and hostname != ip:
                return hostname
        except:
            pass
        
        # Method 2: nslookupコマンドを使用（Docker環境での代替手段）
        try:
            result = subprocess.run(['nslookup', ip], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'name =' in line:
                        hostname = line.split('name =')[-1].strip().rstrip('.')
                        if hostname and hostname != ip:
                            return hostname
        except:
            pass
        
        # Method 3: nmapから取得（利用可能な場合）
        try:
            if hasattr(self, 'nm') and ip in self.nm.all_hosts():
                if 'hostnames' in self.nm[ip]:
                    hostnames = self.nm[ip]['hostnames']
                    if hostnames and len(hostnames) > 0:
                        hostname = hostnames[0].get('name', '')
                        if hostname and hostname != ip:
                            return hostname
        except:
            pass
            
        return None
    
    def _is_running_in_docker(self) -> bool:
        """
        Docker環境内で実行されているかどうかを判定
        """
        try:
            with open('/proc/1/cgroup', 'r') as f:
                return 'docker' in f.read()
        except:
            return False
    
    def _scan_with_ping_validation(self, network_range: str) -> List[Dict]:
        """
        Docker環境での実際のpingベースのスキャン
        """
        devices = []
        import ipaddress
        
        try:
            # CIDR記法を解析
            if '/' in network_range:
                network = ipaddress.IPv4Network(network_range, strict=False)
                ip_list = list(network.hosts())
            elif '-' in network_range:
                # 範囲記法 (例: 192.168.1.1-20)
                start_ip, end_range = network_range.split('-')
                start_parts = start_ip.split('.')
                start_num = int(start_parts[-1])
                end_num = int(end_range)
                base_ip = '.'.join(start_parts[:-1])
                ip_list = [ipaddress.IPv4Address(f"{base_ip}.{i}") for i in range(start_num, end_num + 1)]
            else:
                # 単一IP
                ip_list = [ipaddress.IPv4Address(network_range)]
            
            print(f"検証対象IP数: {len(ip_list)}")
            
            # 並列でpingチェックを実行（最大20並列）
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                future_to_ip = {executor.submit(self._ping_check, str(ip)): str(ip) for ip in ip_list}
                
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip_str = future_to_ip[future]
                    try:
                        is_online = future.result()
                        if is_online:
                            print(f"応答あり: {ip_str}")
                            device_info = {
                                'ip_address': ip_str,
                                'status': 'online',
                                'hostname': self._get_hostname(ip_str),
                                'mac_address': self._get_mac_address(ip_str),
                                'vendor': None  # Docker環境では制限される
                            }
                            devices.append(device_info)
                        else:
                            print(f"応答なし: {ip_str}")
                    except Exception as e:
                        print(f"エラー {ip_str}: {e}")
                    
        except Exception as e:
            print(f"スキャン処理エラー: {e}")
            
        return devices
    
    def _ping_check(self, ip_str: str) -> bool:
        """
        個別IPアドレスのpingチェック
        """
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', ip_str], 
                                  capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            return False
            
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