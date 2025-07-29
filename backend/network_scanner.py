"""
����������_�
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
        �������n_h�����
        """
        if not network_range:
            network_range = NETWORK_SCAN_CONFIG["default_network"]
            
        devices = []
        
        try:
            # ping����L
            self.nm.scan(hosts=network_range, arguments='-sn')
            
            for host in self.nm.all_hosts():
                device_info = {
                    'ip_address': host,
                    'status': 'online' if self.nm[host].state() == 'up' else 'offline',
                    'hostname': self._get_hostname(host),
                    'mac_address': self._get_mac_address(host),
                    'vendor': self._get_vendor(host)
                }
                
                # OS�1n֗�f�
                os_info = self._get_os_info(host)
                if os_info:
                    device_info['os_info'] = os_info
                    
                devices.append(device_info)
                
        except Exception as e:
            print(f"������������: {e}")
            
        return devices
    
    def _get_hostname(self, ip: str) -> Optional[str]:
        """
        IP���K�۹��֗
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except:
            return None
            
    def _get_mac_address(self, ip: str) -> Optional[str]:
        """
        MAC��칒֗ARP	
        """
        try:
            # Linuxgnarp���ɟL
            result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
            if result.returncode == 0:
                # MAC��칒��
                match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', result.stdout)
                if match:
                    return match.group(0)
        except:
            pass
        return None
        
    def _get_vendor(self, ip: str) -> Optional[str]:
        """
        MAC���K������1�֗
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
        OS�1��,
        """
        try:
            # OS������root)P	
            self.nm.scan(hosts=ip, arguments='-O')
            if 'osmatch' in self.nm[ip]:
                os_matches = self.nm[ip]['osmatch']
                if os_matches:
                    return os_matches[0]['name']
        except:
            pass
        return None