import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.roku_controller import RokuController
from modules.ir_controller import IRController
from modules.discovery import DiscoveryService
from config import KEY_MAP_ROKU

class TestRemoteSystem(unittest.TestCase):

    def test_key_map_integrity(self):
        """Verify that basic keys are mapped."""
        self.assertIn("power", KEY_MAP_ROKU)
        self.assertIn("vol_up", KEY_MAP_ROKU)
        print("[PASS] Key Map Integrity")

    def test_roku_controller_instantiation(self):
        """Test if RokuController inits without error."""
        try:
            rc = RokuController("192.168.1.50")
            self.assertEqual(rc.ip_address, "192.168.1.50")
            print("[PASS] RokuController Instantiation")
        except Exception as e:
            self.fail(f"RokuController init failed: {e}")

    def test_ir_controller_instantiation(self):
        """Test if IRController inits without error."""
        try:
            irc = IRController("192.168.1.100")
            self.assertEqual(irc.blaster_ip, "192.168.1.100")
            print("[PASS] IRController Instantiation")
        except Exception as e:
            self.fail(f"IRController init failed: {e}")
            
    def test_discovery_init(self):
        """Test discovery service initialization."""
        ds = DiscoveryService()
        self.assertIsInstance(ds.found_devices, list)
        print("[PASS] DiscoveryService Instantiation")

if __name__ == '__main__':
    unittest.main()
