import socket
import threading
import time
from utils.logger import logger

class SSDPDiscovery:
    """Discovers Roku devices using SSDP."""
    
    SSDP_ADDR = "239.255.255.250"
    SSDP_PORT = 1900
    TARGETS = [
        "roku:ecp",
        "upnp:rootdevice",
        "urn:dial-multiscreen-org:service:dial:1", # Android TV / Chromecast
        "ssdp:all"
    ]

    def __init__(self):
        self.found_devices = []

    def discover(self, timeout=4):
        self.found_devices = []
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0) # Short recv timeout
        
        try:
            for target in self.TARGETS:
                ssdp_request = (
                    'M-SEARCH * HTTP/1.1\r\n' +
                    f'HOST: {self.SSDP_ADDR}:{self.SSDP_PORT}\r\n' +
                    f'MAN: "ssdp:discover"\r\n' +
                    f'MX: 2\r\n' +
                    f'ST: {target}\r\n' + 
                    '\r\n'
                ).encode('utf-8')
                sock.sendto(ssdp_request, (self.SSDP_ADDR, self.SSDP_PORT))
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(2048)
                    self._parse_response(data.decode('utf-8', errors='ignore'), addr)
                except socket.timeout:
                    continue
        except Exception as e:
            logger.error(f"SSDP Discovery error: {e}")
        finally:
            sock.close()
            
        return self.found_devices

    def _parse_response(self, response_text, addr):
        headers = {}
        for line in response_text.split('\r\n'):
            if ':' in line:
                parts = line.split(':', 1)
                headers[parts[0].strip().lower()] = parts[1].strip()
        
        location = headers.get('location', '').lower()
        server = headers.get('server', '').lower()
        st = headers.get('st', '').lower()
        
        ip = addr[0]
        if any(d['ip'] == ip for d in self.found_devices):
            return

        # Identify Device Type
        if 'roku' in server or 'roku' in location:
            self.found_devices.append({
                'ip': ip,
                'name': f"TCL Roku TV ({ip})",
                'type': 'roku'
            })
            logger.info(f"Discovered Roku TV at {ip}")
        elif 'android' in server or 'dial' in server or 'dial' in st:
            self.found_devices.append({
                'ip': ip,
                'name': f"TCL Android TV ({ip})",
                'type': 'android'
            })
            logger.info(f"Discovered Android/DIAL TV at {ip}")
        elif location:
            # Generic Smart TV
            self.found_devices.append({
                'ip': ip,
                'name': f"Smart TV ({ip})",
                'type': 'generic'
            })
            logger.info(f"Discovered Generic SSDP device at {ip}")
