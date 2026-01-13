import threading
import time
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder

# New Structure Imports
from controllers.roku_controller import RokuController
from controllers.ir_controller import IRController
from discovery.ssdp_discovery import SSDPDiscovery
from discovery.esp32_discovery import ESP32Discovery
from services.network_service import send_wol
from services.power_service import PowerService
from android_bridge.wifi_info import get_wifi_details
from utils.storage import Storage
from utils.ui_utils import show_error
from utils.constants import DEFAULT_IR_BLASTER_IP
from utils.logger import logger

class DiscoveryScreen(Screen):
    """Screen for scanning and selecting devices."""
    
    def scan_network(self):
        """Start background discovery for both Roku and ESP32."""
        if not App.get_running_app().wifi_connected:
            show_error("Wi-Fi not connected. Please connect to your home network to scan for TV and Blaster.")
            return

        self.ids.rv_devices.data = [{'text': "Scanning for TV and Blaster..."}]
        
        def run_discovery():
            roku_devices = SSDPDiscovery().discover()
            esp32_devices = ESP32Discovery().discover()
            all_devices = roku_devices + esp32_devices
            Clock.schedule_once(lambda dt: self._update_list(all_devices), 0)

        threading.Thread(target=run_discovery, daemon=True).start()

    def _update_list(self, devices):
        data = []
        if not devices:
            data.append({'text': "No devices found. Ensure Wi-Fi is on."})
        
        for dev in devices:
            type_label = "TV" if dev['type'] != 'ir' else "IR Blaster"
            display_text = f"{dev['name']} ({type_label})\n[size=12sp]{dev['ip']}[/size]"
            data.append({
                'text': display_text,
                'markup': True,
                'on_release': lambda d=dev: App.get_running_app().connect_to_device(d)
            })
        self.ids.rv_devices.data = data

    def connect_ir_manual(self):
        """Connect to fallback IR using saved IP."""
        ip = App.get_running_app().ir_blaster_ip
        dev = {'ip': ip, 'name': "Manual IR Blaster", 'type': 'ir'}
        App.get_running_app().connect_to_device(dev)


class SettingsScreen(Screen):
    """Screen for configurations and about section."""
    def save_settings(self, new_ip):
        App.get_running_app().ir_blaster_ip = new_ip
        logger.info(f"Settings updated. ESP32 IP: {new_ip}")
        App.get_running_app().switch_screen('discovery')

class ControlScreen(Screen):
    """Main remote control interface."""
    pass # Managed via smartremote.kv and App methods

class SmartRemoteApp(App):
    """
    Production-ready logic for TCL Smart Remote.
    Handles auto-connection, Wi-Fi logic, and IR fallback.
    """
    
    # Observables for UI
    connected_device_name = StringProperty("Not Connected")
    connection_status_color = ListProperty([0.5, 0.5, 0.5, 1])
    is_ir_mode = BooleanProperty(False)
    wifi_info_text = StringProperty("Scanning Network...")
    wifi_connected = BooleanProperty(False)
    ir_blaster_ip = StringProperty(DEFAULT_IR_BLASTER_IP)
    
    controller = ObjectProperty(None, allownone=True)
    
    def on_start(self):
        # 1. Detect Wi-Fi SSID
        self._refresh_wifi_status(0)
        logger.info(f"Current Environment Status: {self.wifi_info_text}")
        
        # 2. Attempt Auto-Reconnect
        last_device = Storage.load_last_device()
        if last_device:
            logger.info(f"Auto-reconnecting to {last_device['ip']}...")
            self.connect_to_device(last_device)
        
        # 3. Schedule periodic Wi-Fi check
        Clock.schedule_interval(self._refresh_wifi_status, 10)

    def _refresh_wifi_status(self, dt):
        details = get_wifi_details()
        self.wifi_connected = (details['status'] == "Connected")
        
        if self.wifi_connected:
            # Show SSID and local IP for verification
            self.wifi_info_text = f"Connected: {details['ssid']} ({details['ip']})"
        else:
            self.wifi_info_text = f"Network: {details['status']}"

    def build(self):
        self.title = "SmartRemote"
        self.icon = 'data/icon.png'
        # Explicitly load the renamed KV file
        Builder.load_file('smartremote.kv')
        self.sm = ScreenManager()
        self.sm.add_widget(DiscoveryScreen(name='discovery'))
        self.sm.add_widget(ControlScreen(name='control'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        return self.sm

    def connect_to_device(self, device_info):
        """Initialize appropriate controller and verify connection."""
        ip = device_info['ip']
        self.connected_device_name = f"Connecting to {ip}..."
        
        def connection_task():
            if device_info.get('type') == 'ir':
                new_controller = IRController(ip)
            elif device_info.get('type') == 'android' or device_info.get('type') == 'generic':
                # Android/Generic TVs usually need IR for full control unless ADB is enabled
                show_error(f"Found {device_info['name']}. Direct IP control for Android TV is limited. Switching to IR Blaster fallback.")
                new_controller = IRController(self.ir_blaster_ip)
            else:
                new_controller = RokuController(ip)
            
            if new_controller.connect():
                Clock.schedule_once(lambda dt: self._on_connection_success(new_controller, device_info), 0)
            else:
                Clock.schedule_once(lambda dt: self._on_connection_failure(ip), 0)

        threading.Thread(target=connection_task, daemon=True).start()

    def _on_connection_success(self, controller, dev_info):
        self.controller = controller
        self.connected_device_name = dev_info.get('name', 'Connected Device')
        self.is_ir_mode = isinstance(controller, IRController)
        
        # UI Status Color: Green for Wi-Fi, Orange for IR
        self.connection_status_color = [1, 0.6, 0, 1] if self.is_ir_mode else [0, 0.8, 0.3, 1]
        
        # Persist device metadata (including MAC for WOL)
        dev_info['mac'] = getattr(self.controller, 'mac_address', dev_info.get('mac'))
        Storage.save_last_device(dev_info)
        
        if self.sm.current != 'control':
            self.switch_screen('control')

    def _on_connection_failure(self, ip):
        self.connected_device_name = "Offline / Not Found"
        self.connection_status_color = [0.8, 0.2, 0.2, 1] # Red
        show_error(f"Could not reach {ip}. Is the TV on?")

    def send_command(self, cmd_key):
        """Command routing with Power-On intelligence and Fallback."""
        if cmd_key == "power":
            # If disconnected or Wi-Fi failed, use PowerService which triggers WOL + IR
            if not self.controller or not self.controller.is_connected:
                last_dev = Storage.load_last_device()
                mac = last_dev.get('mac') if last_dev else None
                threading.Thread(target=PowerService.power_on, args=(mac, self.ir_blaster_ip)).start()
                return

        if self.controller:
            threading.Thread(target=self._execute_with_fallback, args=(self.controller.send_key, cmd_key)).start()

    def launch_app(self, app_id):
        """Launch app with fallback logic."""
        if self.controller:
            threading.Thread(target=self._execute_with_fallback, args=(self.controller.launch_app, app_id)).start()

    def _execute_with_fallback(self, func, arg):
        """Executes a command and automatically switches to IR mode if Wi-Fi fails."""
        success = func(arg)
        if not success and not self.is_ir_mode:
            logger.warning("Wi-Fi command failed. Initiating IR Fallback...")
            # Switch internal state to IR
            ir_ctrl = IRController(self.ir_blaster_ip)
            if ir_ctrl.connect():
                self.controller = ir_ctrl
                self.is_ir_mode = True
                self.connection_status_color = [1, 0.6, 0, 1]
                # Retry the command via IR
                self.controller.send_key(arg)
            else:
                Clock.schedule_once(lambda dt: show_error("Connection lost and IR Blaster not found."), 0)

    def switch_screen(self, screen_name):
        self.sm.current = screen_name

    def schedule_task(self, minutes, action):
        """Schedule power off/on."""
        try:
            delay = int(minutes) * 60
            Clock.schedule_once(lambda dt: self.send_command(action), delay)
            logger.info(f"Task scheduled: {action} in {minutes} minutes.")
        except ValueError:
            show_error("Invalid timer value.")

if __name__ == '__main__':
    SmartRemoteApp().run()
