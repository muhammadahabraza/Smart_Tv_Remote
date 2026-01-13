from abc import ABC, abstractmethod

class RemoteController(ABC):
    """Abstract base class for all remote control implementations."""
    
    def __init__(self, ip_address, name="Generic Device"):
        self.ip_address = ip_address
        self.name = name
        self.is_connected = False
        self.mac_address = None

    @abstractmethod
    def connect(self):
        """Establish connection or verify reachability."""
        pass

    @abstractmethod
    def send_key(self, key_code):
        """Send a button press command."""
        pass

    @abstractmethod
    def launch_app(self, app_id):
        """Launch a specific application."""
        pass
