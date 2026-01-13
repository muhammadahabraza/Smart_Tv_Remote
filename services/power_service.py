from services.network_service import send_wol
from controllers.ir_controller import IRController
from utils.logger import logger

class PowerService:
    """Manages Smart Power logic (Wi-Fi + IR fallback)."""

    @staticmethod
    def power_on(mac_address, ir_blaster_ip):
        """Attempts to power on the TV using WOL followed by IR."""
        logger.info("Triggering Power ON sequence...")
        # 1. Try Wake-on-LAN
        wol_success = send_wol(mac_address)
        
        # 2. Trigger IR Command via Blaster (immediate fallback)
        ir = IRController(ir_blaster_ip)
        ir_success = ir.send_key('power')
        
        return wol_success or ir_success

    @staticmethod
    def power_off(controller):
        """Standard Power Off via current active controller."""
        if controller:
            return controller.send_key('power')
        return False
