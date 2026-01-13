from kivy.utils import platform
from utils.logger import logger

def get_wifi_details():
    """Detect current Wi-Fi SSID and IP using Android APIs via Pyjnius."""
    details = {
        'ssid': "Unknown",
        'ip': "0.0.0.0",
        'status': "Disconnected"
    }

    if platform != 'android':
        return {
            'ssid': "Desktop/Simulator",
            'ip': "127.0.0.1",
            'status': "Connected"
        }

    try:
        from jnius import autoclass
        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        
        wifi_manager = activity.getSystemService(Context.WIFI_SERVICE)
        
        if not wifi_manager.isWifiEnabled():
            details['status'] = "Wi-Fi Disabled"
            return details
            
        connection_info = wifi_manager.getConnectionInfo()
        if connection_info.getNetworkId() == -1:
            details['status'] = "Not Connected"
            return details
            
        ssid = connection_info.getSSID()
        if ssid.startswith('"') and ssid.endswith('"'):
            ssid = ssid[1:-1]
        
        if ssid == "<unknown ssid>" or ssid == "0x":
            ssid = "Unknown SSID (Check Permissions)"
            
        # Get IP Address
        ip_int = connection_info.getIpAddress()
        import socket
        import struct
        ip_str = socket.inet_ntoa(struct.pack("<L", ip_int))

        return {
            'ssid': ssid,
            'ip': ip_str,
            'status': "Connected"
        }
    except Exception as e:
        logger.error(f"Failed to get Wi-Fi details on Android: {e}")
        return details
