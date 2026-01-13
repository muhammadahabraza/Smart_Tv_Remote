# Universal Smart TV Remote - QA Validation Checklist

Use this checklist to validate the physical deployment of your system.

## 1. Environment & Network
- [ ] **LAN Connection**: All devices (Phone, TV, ESP32, PC) on same subnet (e.g., 192.168.1.x).
- [ ] **Firewall**: PC blocking incoming UDP (SSDP) on port 1900? (Allow if needed).
- [ ] **Router Isolation**: Disabled "AP Isolation" in router settings? (Critical for Wi-Fi discovery).

## 2. ESP32 IR Blaster
- [ ] **Hardware**: IR LED is correctly wired (Anode to GPIO, Cathode to GND via resistor).
- [ ] **Camera Test**: Point phone camera at IR LED while sending command. Pulse visible?
- [ ] **Serial Output**: Monitor shows "WiFi connected" and an IP address.
- [ ] **API Test**: Visiting `http://<ESP_IP>/ir?code=NEC_0x20DF10EF` (Power) triggers the LED.

## 3. Wi-Fi TV Control (Primary)
- [ ] **Roku ECP**: `http://<TV_IP>:8060/query/device-info` returns XML in browser.
- [ ] **Latency**: Button press on app -> TV reaction is < 200ms.
- [ ] **Key Map**: "Back" and "Home" buttons function correctly.

## 4. IR Fallback (Offline)
- [ ] **Disconnect**: Unplug TV Ethernet/disconnect TV Wi-Fi.
- [ ] **Switch Mode**: Select "IR Blaster" in App Discovery screen.
- [ ] **Control**: Volume/Power commands still work via ESP32.

## 5. App Launch
- [ ] **YouTube**: Opens immediately via Wi-Fi.
- [ ] **Netflix**: Opens immediately via Wi-Fi.

## 6. Auto-Discovery
- [ ] **Scan**: Pressing "Scan" finds Roku TV within 3 seconds.
- [ ] **Restart**: Closing and reopening app finds TV again.

## 7. Android APK
- [ ] **Install**: APK installs via ADB (`adb install bin/package.apk`) or File Manager.
- [ ] **Permissions**: App prompts for Network permissions (if Android 13+ requires it).

## 8. UI / UX
- [ ] **Touch**: Buttons have visual pressed state.
- [ ] **Layout**: UI scales correctly on phone screen (no cut-off buttons).

## 9. Stability
- [ ] **Stress Test**: Mash volume button repeatedly. App should not crash.
- [ ] **Background**: Minimize app, restore app. Connection persists.

## 10. Security
- [ ] **Leak Test**: No data sent to external servers (only local IPs).

## 11. Expansion
- [ ] **New Brand**: `vidaa_controller.py` logic is separate from `roku_controller_py`.
