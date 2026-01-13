import requests
import threading
import socket
from utils.logger import logger

class ESP32Discovery:
    """Discovers ESP32 IR Blasters via HTTP ping on local subnet."""

    def __init__(self):
        self.found_devices = []

    def discover(self):
        self.found_devices = []
        lock = threading.Lock()
        
        try:
            # 1. Get Local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Use a dummy address to get local IP
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                logger.info(f"System Local IP detected: {local_ip}")
            except:
                local_ip = "192.168.18.1" # Default to user's known network
            finally:
                s.close()
            
            # Check for multiple possible subnets (User is on .18.x)
            possible_subnets = ["192.168.18", "192.168.1"]
            current_subnet = ".".join(local_ip.split(".")[:-1])
            if current_subnet not in possible_subnets:
                possible_subnets.insert(0, current_subnet)

            threads = []
            semaphore = threading.BoundedSemaphore(100) # Highly aggressive
            
            for subnet in possible_subnets:
                logger.info(f"Scanning subnet {subnet}.0/24 for TCL IR Blaster...")
                for i in range(1, 255):
                    ip = f"{subnet}.{i}"
                    if ip == local_ip: continue
                    
                    def scoped_ping(target_ip):
                        with semaphore:
                            self._ping_esp32(target_ip, lock)

                    t = threading.Thread(target=scoped_ping, args=(ip,))
                    t.daemon = True
                    t.start()
                    threads.append(t)
            
            # Wait for threads
            import time
            time.sleep(2.0)
            
        except Exception as e:
            logger.error(f"ESP32 Discovery error: {e}")
            
        logger.info(f"ESP32 Discovery found {len(self.found_devices)} devices")
        return self.found_devices

    def _ping_esp32(self, ip, lock):
        try:
            resp = requests.get(f"http://{ip}/ping", timeout=0.8)
            if resp.status_code == 200 and "pong" in resp.text.lower():
                with lock:
                    if not any(d['ip'] == ip for d in self.found_devices):
                        self.found_devices.append({
                            'ip': ip,
                            'name': f"ESP32 Blaster ({ip})",
                            'type': 'ir'
                        })
                        logger.info(f"Found ESP32 Blaster at {ip}")
        except:
            pass
