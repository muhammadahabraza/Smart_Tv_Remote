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

        # Clear previous results and show scanning message
        self.ids.rv_devices.data = [{'text': "Scanning network for TCL devices..."}]
        logger.info("User initiated network scan")
        
        def run_discovery():
            logger.info("Starting SSDP discovery for TVs...")
            roku_devices = SSDPDiscovery().discover()
            logger.info(f"SSDP found {len(roku_devices)} TV(s)")
            
            logger.info("Starting ESP32 discovery for IR Blasters...")
            esp32_devices = ESP32Discovery().discover()
            logger.info(f"ESP32 scan found {len(esp32_devices)} blaster(s)")
            
            all_devices = roku_devices + esp32_devices
            Clock.schedule_once(lambda dt: self._update_list(all_devices), 0)

        threading.Thread(target=run_discovery, daemon=True).start()

    def _update_list(self, devices):
        data = []
        if not devices:
            data.append({'text': "No devices found. Ensure Wi-Fi is on and TV is powered."})
        else:
            logger.info(f"Displaying {len(devices)} discovered device(s)")
        
        for dev in devices:
            # Auto-update IR Blaster IP if found during scan
            if dev['type'] == 'ir':
                App.get_running_app().ir_blaster_ip = dev['ip']
                logger.info(f"Auto-configured IR Blaster IP to {dev['ip']}")

            # Create detailed display text
            if dev['type'] == 'ir':
                type_label = "TCL IR Blaster"
                icon = "🔴"
            elif dev['type'] == 'roku':
                type_label = "TCL Roku TV"
                icon = "📺"
            elif dev['type'] == 'android':
                type_label = "TCL Android TV"
                icon = "📱"
            else:
                type_label = "TCL Smart TV"
                icon = "📺"
            
            display_text = f"{icon} {dev['name']}\n[size=12sp]{type_label} • {dev['ip']}[/size]"
            data.append({
                'text': display_text,
                'markup': True,
                'on_release': lambda d=dev: App.get_running_app().connect_to_device(d)
            })
        
        self.ids.rv_devices.data = data
        logger.info("Device list updated in UI")

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
    blaster_status = StringProperty("Searching for Blaster...")
    blaster_found = BooleanProperty(False)
    
    controller = ObjectProperty(None, allownone=True)
    
    def on_start(self):
        # 1. Detect Wi-Fi SSID
        self._refresh_wifi_status(0)
        logger.info(f"Current Environment Status: {self.wifi_info_text}")
        
        # 2. Skip auto-reconnect - let user scan for fresh devices
        # This ensures the discovery screen shows current network state
        logger.info("Skipping auto-reconnect. User will scan for devices.")
        
        # 3. Schedule periodic Wi-Fi check and initial Blaster search
        Clock.schedule_interval(self._refresh_wifi_status, 10)
        threading.Thread(target=self._initial_blaster_search, daemon=True).start()

    def _initial_blaster_search(self):
        """Silently find the IR Blaster in the background at startup."""
        self.blaster_status = "Scanning network..."
        logger.info("Starting background search for TCL IR Blaster...")
        
        # 1. Try currently set IP
        test_ctrl = IRController(self.ir_blaster_ip)
        if test_ctrl.connect():
            self.blaster_status = f"Blaster Online: {self.ir_blaster_ip}"
            self.blaster_found = True
            return

        # 2. Aggressive Multi-Subnet Scan
        from discovery.esp32_discovery import ESP32Discovery
        blasters = ESP32Discovery().discover()
        
        if blasters:
            self.ir_blaster_ip = blasters[0]['ip']
            self.blaster_status = f"Blaster Found: {self.ir_blaster_ip}"
            self.blaster_found = True
            logger.info(f"Auto-configured Blaster to {self.ir_blaster_ip}")
            # Refresh controller if active
            if self.is_ir_mode and self.controller:
                self.controller.ip_address = self.ir_blaster_ip
        else:
            self.blaster_status = "Blaster Offline (Check Blue Light)"
            self.blaster_found = False

    def _refresh_wifi_status(self, dt):
        details = get_wifi_details()
        self.wifi_connected = (details['status'] == "Connected")
        
        if self.wifi_connected:
            # Show SSID and local IP for verification
            self.wifi_info_text = f"Connected: {details['ssid']} ({details['ip']})"
        else:
            self.wifi_info_text = f"Network: {details['status']}"

    def build(self):
        self.title = "TCL Smart Remote"
        self.icon = 'data/icon.png'
        # smartremote.kv is auto-loaded based on class name SmartRemoteApp
        self.sm = ScreenManager()
        self.sm.add_widget(DiscoveryScreen(name='discovery'))
        self.sm.add_widget(ControlScreen(name='control'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        return self.sm

    def connect_to_device(self, device_info):
        """Initialize appropriate controller and verify connection."""
        ip = device_info['ip']
        dev_type = device_info.get('type', 'unknown')
        self.connected_device_name = f"Connecting to {ip}..."
        logger.info(f"Connection attempt: {ip} (Type: {dev_type})")
        
        def connection_task():
            if dev_type == 'ir':
                new_controller = IRController(ip)
            elif dev_type == 'android' or dev_type == 'generic':
                logger.info(f"Android/Generic TV detected ({ip}). Requiring IR Blaster for control.")
                # We prioritize the blaster IP entered in settings
                new_controller = IRController(self.ir_blaster_ip)
                # For Android, we ALWAYS succeed the 'connection' to the UI
                # but we will show the status of the Blaster separately.
                new_controller.connect() # Try it, but don't block on failure
                Clock.schedule_once(lambda dt: self._on_connection_success(new_controller, device_info), 0)
                return
            else:
                new_controller = RokuController(ip)
            
            logger.info(f"Calling connect() on {type(new_controller).__name__}")
            if new_controller.connect():
                logger.info("Connection successful!")
                Clock.schedule_once(lambda dt: self._on_connection_success(new_controller, device_info), 0)
            else:
                logger.error(f"Connection failed for controller: {type(new_controller).__name__}")
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

    def test_blaster(self, ip):
        """Manually test an IR Blaster IP and show feedback."""
        self.ir_blaster_ip = ip
        logger.info(f"Manually testing IR Blaster at {ip}...")
        
        def test_task():
            test_ctrl = IRController(ip)
            if test_ctrl.connect():
                logger.info("IR Blaster Test Success!")
                show_error(f"Success! IR Blaster found at {ip}. You can now control your TCL TV.")
            else:
                logger.error("IR Blaster Test Failed.")
                show_error(f"Failed to reach IR Blaster at {ip}. Check the blue light and ensure it's on your Wi-Fi.")
        
        threading.Thread(target=test_task, daemon=True).start()

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
