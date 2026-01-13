import requests
from controllers.base_controller import RemoteController
from utils.constants import TCL_IR_CODES
from utils.logger import logger

class IRController(RemoteController):
    """Fallback controller that sends commands to an ESP32-based IR blaster."""
    
    def __init__(self, blaster_ip):
        super().__init__(blaster_ip, "IR Blaster")
        self.blaster_ip = blaster_ip

    def connect(self):
        try:
            # Simple ping to check if ESP32 is alive
            resp = requests.get(f"http://{self.blaster_ip}/ping", timeout=2)
            self.is_connected = resp.status_code == 200
            return self.is_connected
        except:
            self.is_connected = False
            return False

    def send_key(self, key_code):
        code = TCL_IR_CODES.get(key_code)
        if not code:
            logger.warning(f"IR Code for {key_code} not found.")
            return False

        try:
            url = f"http://{self.blaster_ip}/ir"
            requests.get(url, params={"code": code}, timeout=1)
            return True
        except Exception as e:
            logger.error(f"Failed to send IR command: {e}")
            return False

    def launch_app(self, app_id):
        # IR fallback usually can't launch apps directly, might use 'Home' as fallback
        logger.info("Direct app launch not supported via IR. Routing to Home.")
        return self.send_key('home')
