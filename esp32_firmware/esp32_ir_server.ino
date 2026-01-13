#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <Preferences.h>

// ================= DEVICE CONFIGURATION =================
const char* ap_ssid = "SmartRemote_Config"; // SSID of the AP if WiFi fails
const char* hostname = "irblaster"; 
const uint16_t kIrLed = 4; 
// ========================================================

WebServer server(80);
IRsend irsend(kIrLed);
Preferences preferences;

void setup() {
  Serial.begin(115200);
  irsend.begin();

  // Initialize Preferences (nvs storage)
  preferences.begin("wifi-creds", false);
  String stored_ssid = preferences.getString("ssid", "");
  String stored_pass = preferences.getString("pass", "");

  WiFi.mode(WIFI_STA);
  
  bool connected = false;
  if (stored_ssid != "") {
    Serial.println("Attempting connection to stored WiFi: " + stored_ssid);
    WiFi.begin(stored_ssid.c_str(), stored_pass.c_str());
    
    // Wait for connection with a 10-second timeout
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    connected = (WiFi.status() == WL_CONNECTED);
  }

  if (connected) {
    Serial.println("\nWiFi Connected! IP: " + WiFi.localIP().toString());
    startMainServer();
  } else {
    Serial.println("\nWiFi Connection Failed. Starting Access Point...");
    startConfigPortal();
  }
}

void loop() {
  server.handleClient();
  // Optional: Blinking LED in loop if in AP mode
}

void startMainServer() {
  if (MDNS.begin(hostname)) {
    Serial.println("MDNS responder started: " + String(hostname) + ".local");
  }
  
  server.on("/", handleRoot);
  server.on("/ir", handleIr);
  server.on("/ping", [](){ server.send(200, "text/plain", "pong"); });
  server.begin();
}

void startConfigPortal() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ap_ssid);
  Serial.println("AP Started. Connect to: " + String(ap_ssid));
  Serial.println("AP IP: " + WiFi.softAPIP().toString());

  server.on("/", handleConfigRoot);
  server.on("/save", handleWifiSave);
  server.begin();
}

void handleConfigRoot() {
  String html = "<html><body><h1>SmartRemote Config</h1>";
  html += "<form action='/save' method='POST'>";
  html += "SSID: <input type='text' name='ssid'><br>";
  html += "Pass: <input type='password' name='pass'><br>";
  html += "<input type='submit' value='Save & Connect'>";
  html += "</form></body></html>";
  server.send(200, "text/html", html);
}

void handleWifiSave() {
  if (server.hasArg("ssid") && server.hasArg("pass")) {
    String new_ssid = server.arg("ssid");
    String new_pass = server.arg("pass");
    
    preferences.putString("ssid", new_ssid);
    preferences.putString("pass", new_pass);
    
    server.send(200, "text/plain", "Credentials Saved. Rebooting...");
    delay(2000);
    ESP.restart();
  } else {
    server.send(400, "text/plain", "Missing SSID or PASS");
  }
}

void handleRoot() {
  server.send(200, "text/plain", "ESP32 IR Blaster Ready. Usage: /ir?code=NEC_0x12345678");
}

void handleIr() {
  if (server.hasArg("code")) {
    String codeStr = server.arg("code");
    Serial.println("IR Request: " + codeStr);

    int splitIndex = codeStr.indexOf('_');
    if (splitIndex == -1) {
      server.send(400, "text/plain", "Invalid Format. Use PROTOCOL_HEX");
      return;
    }

    String protocol = codeStr.substring(0, splitIndex);
    String hexValStr = codeStr.substring(splitIndex + 1);
    uint64_t data = strtoull(hexValStr.c_str(), NULL, 16);

    if (protocol.equalsIgnoreCase("NEC")) {
        irsend.sendNEC(data, 32); 
        server.send(200, "text/plain", "Sent NEC: " + hexValStr);
    } 
    else if (protocol.equalsIgnoreCase("SAMSUNG")) {
        irsend.sendSamsung(data, 32);
        server.send(200, "text/plain", "Sent Samsung: " + hexValStr);
    }
    else {
        server.send(400, "text/plain", "Protocol not supported.");
    }
  } else {
    server.send(400, "text/plain", "Missing 'code'");
  }
}
