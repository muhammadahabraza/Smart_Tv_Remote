# TCL Smart Remote

A production-ready Android application built with Kivy and Python to control TCL Smart TVs via Wi-Fi (ECP) with a seamless ESP32-based IR fallback.

## 🚀 Features

- **Auto-Discovery**: Automatically finds Roku-based TCL TVs via SSDP and ESP32 IR Blasters via HTTP ping.
- **Smart Power**: Turns the TV ON using Wake-on-LAN (WOL) and IR signals simultaneously for maximum reliability.
- **IR Fallback**: Automatically switches to IR mode if the TV becomes unreachable via Wi-Fi.
- **App Shortcuts**: Quick launch for Netflix, YouTube, and Prime Video.
- **Android Integration**: Detects current Wi-Fi SSID to ensure the phone and TV are on the same network.

## 📂 Project Structure

- `main.py`: Application entry point and state management.
- `smartremote.kv`: Premium UI design with dark mode and status indicators.
- `controllers/`: Hardware-specific control logic (Roku/ECP and IR/ESP32).
- `discovery/`: Network scanning services.
- `services/`: High-level logic for Power and Network management.
- `android_bridge/`: Pyjnius-based Android system integrations.
- `utils/`: Common utilities (storage, logging, constants).
- `data/`: App assets (icons, splash screens).
- `esp32_firmware/`: Arduino source code for the IR Blaster hardware.

## 🛠 Setup & Build

### Requirements
- Python 3.10+
- Kivy 2.3.0
- Buildozer (for Android builds)

### Building the APK
```bash
buildozer android debug
```

## 🔋 Hardware (ESP32 IR Blaster)
Flash the code in `esp32_firmware/esp32_ir_server.ino` to an ESP32 with an IR LED connected to GPIO 4. The app will automatically find it on your local network.

---
**Status**: READY TO BUILD 🟢
