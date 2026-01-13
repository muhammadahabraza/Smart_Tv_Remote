# Constants and Configuration for SmartRemote

# Colors shifted to Kivy KV file for styling, but kept here for logic if needed
DEFAULT_IR_BLASTER_IP = "192.168.1.100"
DISCOVERY_TIMEOUT = 3.0

# Key Mappings (Internal internal_key -> Roku key string)
KEY_MAP_ROKU = {
    "power": "Power",
    "home": "Home",
    "back": "Back",
    "select": "Select",
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
    "play": "Play",
    "pause": "Play",
    "rev": "Rev",
    "fwd": "Fwd",
    "vol_up": "VolumeUp",
    "vol_down": "VolumeDown",
    "mute": "VolumeMute",
    "enter": "Enter",
}

# TCL IR Codes (Placeholders - based on common NEC codes for TCL)
# Format: PROTOCOL_HEX
TCL_IR_CODES = {
    "power": "NEC_0x40BF12ED",
    "vol_up": "NEC_0x40BF40BF",
    "vol_down": "NEC_0x40BFC03F",
    "mute": "NEC_0x40BF31CE",
    "up": "NEC_0x40BF10EF",
    "down": "NEC_0x40BF906F",
    "left": "NEC_0x40BFD02F",
    "right": "NEC_0x40BF50AF",
    "select": "NEC_0x40BF30CF",
    "back": "NEC_0x40BF11EE",
    "home": "NEC_0x40BF33CC",
}
