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

        # Identify Device Type - TCL specific filters
        device_name = None
        device_type = None
        
        if 'roku' in server or 'roku' in location:
            device_type = 'roku'
            # Try to get actual device name from Roku
            device_name = self._get_roku_device_name(ip)
            if not device_name:
                device_name = f"TCL Roku TV"
        elif 'android' in server or 'dial' in server or 'dial' in st:
            device_type = 'android'
            device_name = self._get_device_name_from_location(headers.get('location', ''))
            if not device_name:
                device_name = f"TCL Android TV"
        elif 'espressif' in server or ':80' in location:
            # Don't label the IR blaster as TCL
            return
        elif location:
            device_type = 'generic'
            device_name = self._get_device_name_from_location(headers.get('location', ''))
            if not device_name:
                device_name = f"TCL Smart TV"
        else:
            return
        
        self.found_devices.append({
            'ip': ip,
            'name': device_name,
            'type': device_type
        })
        logger.info(f"Discovered {device_name} at {ip}")

    def _get_roku_device_name(self, ip):
        """Fetch actual device name from Roku ECP."""
        try:
            import requests
            resp = requests.get(f"http://{ip}:8060/query/device-info", timeout=2)
            if resp.status_code == 200:
                # Simple XML parsing
                content = resp.text
                # Extract friendly name
                name_start = content.find('<user-device-name>')
                if name_start != -1:
                    name_start += len('<user-device-name>')
                    name_end = content.find('</user-device-name>', name_start)
                    if name_end != -1:
                        return content[name_start:name_end].strip()
                
                # Fallback to model name
                model_start = content.find('<model-name>')
                if model_start != -1:
                    model_start += len('<model-name>')
                    model_end = content.find('</model-name>', model_start)
                    if model_end != -1:
                        return content[model_start:model_end].strip()
        except:
            pass
        return None

    def _get_device_name_from_location(self, location_url):
        """Try to fetch device name from UPnP description XML."""
        if not location_url:
            return None
        try:
            import requests
            resp = requests.get(location_url, timeout=2)
            if resp.status_code == 200:
                content = resp.text
                # Try to find friendlyName
                name_start = content.find('<friendlyName>')
                if name_start != -1:
                    name_start += len('<friendlyName>')
                    name_end = content.find('</friendlyName>', name_start)
                    if name_end != -1:
                        return content[name_start:name_end].strip()
        except:
            pass
        return None
