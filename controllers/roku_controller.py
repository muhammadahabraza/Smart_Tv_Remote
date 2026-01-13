import requests
from controllers.base_controller import RemoteController
from utils.constants import KEY_MAP_ROKU
from utils.logger import logger

class RokuController(RemoteController):
    """Controls Roku-based TCL TVs via External Control Protocol (ECP)."""

    def __init__(self, ip_address, port=8060):
        super().__init__(ip_address, "Roku TV")
        self.port = port
        self.base_url = f"http://{ip_address}:{port}"

    def connect(self):
        try:
            resp = requests.get(f"{self.base_url}/query/device-info", timeout=3)
            if resp.status_code == 200:
                self.is_connected = True
                content = resp.text
                self.mac_address = self._extract_xml(content, "wifi-mac")
                self.model_name = self._extract_xml(content, "model-name")
                self.name = self.model_name if self.model_name else "Roku TV"
                return True
        except Exception as e:
            logger.error(f"Roku connect failed: {e}")
        
        self.is_connected = False
        return False

    def _extract_xml(self, xml, tag):
        start = xml.find(f"<{tag}>")
        if start == -1: return None
        start += len(tag) + 2
        end = xml.find(f"</{tag}>", start)
        return xml[start:end]

    def send_key(self, key_code):
        roku_key = KEY_MAP_ROKU.get(key_code)
        if not roku_key:
            logger.warning(f"Key {key_code} not mapped for Roku")
            return False
            
        try:
            url = f"{self.base_url}/keypress/{roku_key}"
            requests.post(url, timeout=1)
            return True
        except Exception as e:
            logger.error(f"Roku send_key failed: {e}")
            return False

    def launch_app(self, app_id):
        try:
            url = f"{self.base_url}/launch/{app_id}"
            requests.post(url, timeout=2)
            return True
        except Exception as e:
            logger.error(f"Roku launch_app failed: {e}")
            return False
