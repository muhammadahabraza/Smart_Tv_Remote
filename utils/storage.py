import json
import os
from kivy.app import App
from utils.logger import logger

class Storage:
    """Handles persistence of device settings and last connected device."""
    
    @staticmethod
    def _get_path():
        # Use application data directory for persistence on Android
        return os.path.join(App.get_running_app().user_data_dir, "config.json")

    @classmethod
    def save_last_device(cls, device_info):
        try:
            with open(cls._get_path(), 'w') as f:
                json.dump(device_info, f)
        except Exception as e:
            logger.error(f"Storage Save Error: {e}")

    @classmethod
    def load_last_device(cls):
        path = cls._get_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Storage Load Error: {e}")
        return None
