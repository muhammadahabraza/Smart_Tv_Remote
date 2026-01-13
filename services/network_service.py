import socket
import struct
from utils.logger import logger

def send_wol(mac_address):
    """Sends Wake-on-LAN magic packet to specified MAC address."""
    if not mac_address:
        return False
        
    try:
        # Format MAC: AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF
        mac_address = mac_address.replace(':', '').replace('-', '')
        if len(mac_address) != 12:
            raise ValueError("Invalid MAC address length")
            
        # Create magic packet
        data = bytes.fromhex('F' * 12 + mac_address * 16)
        
        # Broadcast to network
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ('<broadcast>', 9))
        sock.close()
        logger.info(f"WOL magic packet sent to {mac_address}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WOL: {e}")
        return False

def check_reachability(ip, port=8060):
    """Check if a specific host:port is reachable."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False
