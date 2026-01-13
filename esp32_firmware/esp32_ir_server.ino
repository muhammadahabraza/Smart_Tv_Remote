#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <Preferences.h>

// ================= DEVICE CONFIGURATION =================
const char* ap_ssid = "TCL_Remote_Setup"; 
const uint16_t kIrLed = 4;      // IR LED Pin
const uint16_t kStatusLed = 2;  // Built-in Blue LED for Status
// ========================================================

WebServer server(80);
IRsend irsend(kIrLed);
Preferences preferences;

void setup() {
  pinMode(kStatusLed, OUTPUT);
  Serial.begin(115200);
  irsend.begin();

  preferences.begin("wifi-creds", false);
  String stored_ssid = preferences.getString("ssid", "");
  String stored_pass = preferences.getString("pass", "");

  WiFi.mode(WIFI_STA);
  
  if (stored_ssid != "") {
    Serial.println("Connecting to: " + stored_ssid);
    WiFi.begin(stored_ssid.c_str(), stored_pass.c_str());
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      digitalWrite(kStatusLed, !digitalRead(kStatusLed)); // Fast blink during connection
      delay(250);
      Serial.print(".");
      attempts++;
    }
  }

  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(kStatusLed, HIGH); // SOLID BLUE = SUCCESS
    Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
    startMainServer();
  } else {
    digitalWrite(kStatusLed, LOW); // LED OFF = Entering Setup Mode
    Serial.println("\nConnection Failed. Starting Setup Portal...");
    startConfigPortal();
  }
}

void loop() {
  server.handleClient();
  if (WiFi.status() != WL_CONNECTED && WiFi.getMode() == WIFI_AP) {
    // Slow pulse in AP mode to show it's waiting for user
    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate > 1000) {
      digitalWrite(kStatusLed, !digitalRead(kStatusLed));
      lastUpdate = millis();
    }
  }
}

void startMainServer() {
  MDNS.begin("tclblaster");
  server.on("/", [](){ server.send(200, "text/plain", "TCL Blaster Ready"); });
  server.on("/ping", [](){ server.send(200, "text/plain", "pong"); });
  server.on("/ir", handleIr);
  server.on("/reset", [](){
      preferences.clear();
      server.send(200, "text/plain", "Resetting Wi-Fi... Rebooting.");
      delay(1000);
      ESP.restart();
  });
  server.begin();
}

void startConfigPortal() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ap_ssid);
  
  server.on("/", handleConfigRoot);
  server.on("/save", handleWifiSave);
  server.begin();
}

void handleConfigRoot() {
  String html = "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<style>body{font-family:sans-serif;background:#121212;color:white;padding:20px;}";
  html += "input{width:100%;padding:10px;margin:10px 0;border-radius:5px;border:none;}";
  html += "input[type='submit']{background:#e60012;color:white;font-weight:bold;}</style></head><body>";
  html += "<h1>TCL Remote Setup</h1><p>Select your Wi-Fi network:</p>";
  
  html += "<form action='/save' method='POST'>";
  html += "SSID: <input type='text' name='ssid' id='ssid' placeholder='SSID Name'><br>";
  html += "Password: <input type='password' name='pass' placeholder='Password'><br>";
  html += "<input type='submit' value='CONNECT TO WIFI'></form>";
  
  html += "<h3>Nearby Networks:</h3><ul style='color:#aaa'>";
  int n = WiFi.scanNetworks();
  for (int i = 0; i < n; ++i) {
    html += "<li>" + WiFi.SSID(i) + " (" + String(WiFi.RSSI(i)) + "dBm)</li>";
  }
  html += "</ul></body></html>";
  server.send(200, "text/html", html);
}

void handleWifiSave() {
  if (server.hasArg("ssid")) {
    preferences.putString("ssid", server.arg("ssid"));
    preferences.putString("pass", server.arg("pass"));
    server.send(200, "text/html", "<html><body><h3>Saved!</h3><p>Blaster is rebooting to connect to " + server.arg("ssid") + ". Look for the <b>Solid Blue Light</b>.</p></body></html>");
    delay(2000);
    ESP.restart();
  }
}

void handleIr() {
  if (server.hasArg("code")) {
    String codeStr = server.arg("code");
    // Pulse status LED to show ingestion
    digitalWrite(kStatusLed, LOW); 
    
    int splitIndex = codeStr.indexOf('_');
    String protocol = codeStr.substring(0, splitIndex);
    String hexValStr = codeStr.substring(splitIndex + 1);
    uint64_t data = strtoull(hexValStr.c_str(), NULL, 16);

    if (protocol.equalsIgnoreCase("NEC")) {
        irsend.sendNEC(data, 32); 
    } else if (protocol.equalsIgnoreCase("SAMSUNG")) {
        irsend.sendSamsung(data, 32);
    }
    
    digitalWrite(kStatusLed, HIGH); 
    server.send(200, "text/plain", "Sent");
  }
}
