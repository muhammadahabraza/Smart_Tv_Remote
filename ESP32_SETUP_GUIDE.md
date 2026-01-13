# ESP32 IR Blaster - Complete Setup Guide

## What You Need
- ESP32 Development Board (any model with Wi-Fi)
- IR LED (940nm recommended)
- 100-220Ω Resistor
- Jumper wires
- USB cable for programming

## Hardware Wiring

```
ESP32 GPIO 4 ----[Resistor]---- IR LED (Anode +)
                                    |
ESP32 GND ---------------------- IR LED (Cathode -)

ESP32 GPIO 2 = Built-in Blue LED (Status Indicator)
```

**Important**: The IR LED must point directly at your TV's IR receiver (usually bottom center of the TV).

## Software Setup

### Step 1: Install Arduino IDE
1. Download from: https://www.arduino.cc/en/software
2. Install and open Arduino IDE

### Step 2: Add ESP32 Board Support
1. Go to **File > Preferences**
2. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Go to **Tools > Board > Boards Manager**
4. Search for "esp32" and install **"esp32 by Espressif Systems"**

### Step 3: Install Required Libraries
1. Go to **Sketch > Include Library > Manage Libraries**
2. Search and install:
   - **IRremoteESP8266** (by David Conran)
   - **Preferences** (built-in, no install needed)

### Step 4: Flash the Firmware
1. Open `esp32_ir_server.ino` from your project folder
2. Connect ESP32 to your computer via USB
3. Select your board:
   - **Tools > Board > ESP32 Arduino > ESP32 Dev Module**
4. Select the correct port:
   - **Tools > Port > COM# (ESP32)**
5. Click **Upload** (→ button)

### Step 5: Monitor Status
1. Open **Tools > Serial Monitor**
2. Set baud rate to **115200**
3. Press the **EN/RESET** button on your ESP32
4. Watch for these messages:

**Success Messages:**
```
Connecting to: YourWiFiName
.....
Connected! IP: 192.168.18.XXX
```

**Setup Mode Messages:**
```
Connection Failed. Starting Setup Portal...
```

## Wi-Fi Configuration

### Method 1: Auto-Setup Portal (Recommended)
1. If ESP32 can't connect, it creates a hotspot: **`TCL_Remote_Setup`**
2. Connect your phone to this network
3. A setup page should auto-open (or go to `192.168.4.1`)
4. You'll see a list of nearby Wi-Fi networks
5. Select your home network and enter the password
6. Click **CONNECT TO WIFI**
7. ESP32 will reboot and connect

### Method 2: Manual Configuration (Advanced)
Edit the firmware before uploading:
```cpp
// In esp32_ir_server.ino, add these lines in setup():
WiFi.begin("YOUR_WIFI_NAME", "YOUR_PASSWORD");
```

## LED Status Indicators

| LED Behavior | Meaning |
|--------------|---------|
| **Fast Blinking** | Trying to connect to Wi-Fi |
| **Slow Pulse** | Setup mode (waiting for configuration) |
| **Solid Blue** | ✅ Connected to Wi-Fi successfully |
| **Off** | No power or firmware not running |
| **Quick Flash** | IR command sent |

## Testing the Blaster

### Test 1: Check Connection
Open your browser and go to:
```
http://192.168.18.XXX/ping
```
(Replace XXX with the IP shown in Serial Monitor)

**Expected Response:** `pong`

### Test 2: Send IR Command
```
http://192.168.18.XXX/ir?code=NEC_0x40BF12ED
```
**Expected:** TV should turn on/off, LED should flash

### Test 3: Camera Test
1. Open your phone camera
2. Point it at the IR LED
3. Send a command from the app
4. You should see a **purple/white flicker** on camera (IR is invisible to eyes)

## Troubleshooting

### Problem: No lights at all
- **Check USB power**: Try a different cable or power source
- **Check wiring**: Ensure GPIO 2 is not shorted
- **Re-flash firmware**: Upload the code again

### Problem: Blinking but never solid
- **Wrong Wi-Fi password**: Reset and reconfigure
- **Router issues**: Check if MAC filtering is enabled
- **Signal strength**: Move ESP32 closer to router

### Problem: Solid light but app can't connect
- **Wrong subnet**: ESP32 might be on 5GHz, phone on 2.4GHz
- **Firewall**: Check router firewall settings
- **IP changed**: Check Serial Monitor for current IP

### Problem: Commands don't work on TV
- **Wrong IR codes**: TCL models vary, codes might need adjustment
- **LED positioning**: Point directly at TV sensor
- **LED polarity**: Swap anode/cathode if backwards
- **Resistor value**: Try 100Ω if 220Ω is too dim

## Reset to Factory
To clear saved Wi-Fi and start over:
```
http://192.168.18.XXX/reset
```
ESP32 will reboot into setup mode.

## Advanced: Finding Your ESP32's IP

### Method 1: Serial Monitor
The IP is printed when it connects.

### Method 2: Router Admin Page
1. Log into your router (usually `192.168.1.1` or `192.168.18.1`)
2. Look for connected devices
3. Find device named **"tclblaster"** or **"espressif"**

### Method 3: Network Scanner
Use an app like "Fing" or "Network Scanner" on your phone.

## Next Steps
Once the blue LED is **solid** and you can access `/ping`:
1. Note the IP address
2. Open the TCL Smart Remote app
3. Go to Settings (⚙)
4. Enter the IP address
5. Click **TEST**
6. You should see "Success!"

---

**Need Help?** Check the Serial Monitor output—it tells you exactly what's happening!
