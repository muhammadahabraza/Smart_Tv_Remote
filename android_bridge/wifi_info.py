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
        from jnius import autoclass, cast
        from android.permissions import request_permissions, Permission
        
        # 1. Request Runtime Location Permission (Required for SSID on Android 10+)
        def check_permissions():
            request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        
        # Note: In a production app, we'd wait for the callback, 
        # but here we request and then continue to attempt reading.
        check_permissions()

        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        
        # Use ConnectivityManager to check connection status first
        connectivity_manager = activity.getSystemService(Context.CONNECTIVITY_SERVICE)
        active_network = connectivity_manager.getActiveNetworkInfo()
        
        if active_network is None or not active_network.isConnected():
            details['status'] = "Disconnected"
            return details

        # Check if it's Wi-Fi
        if active_network.getType() != 1: # TYPE_WIFI
            details['status'] = "Not on Wi-Fi"
            return details

        # Get Wi-Fi specific info
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
        
        if ssid == "<unknown ssid>" or ssid == "0x" or not ssid:
            ssid = "Connected (SSID Hidden)"
            
        # Get IP Address
        ip_int = connection_info.getIpAddress()
        import socket
        import struct
        # Handle endianness for IP address conversion
        ip_str = socket.inet_ntoa(struct.pack("<L", ip_int))

        return {
            'ssid': ssid,
            'ip': ip_str,
            'status': "Connected"
        }
    except Exception as e:
        logger.error(f"Failed to get Wi-Fi details on Android: {e}")
        return details
