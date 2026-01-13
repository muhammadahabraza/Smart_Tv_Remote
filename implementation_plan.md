# Smart Universal Remote - Implementation Plan

## 1. System Architecture

The application will be built using a modular architecture to separate UI, Logic, Network, and Hardware abstraction layers.

### Layers:
1.  **Presentation Layer (UI)**: Built with **Kivy**. Handles user touch events and displays status.
2.  **Logic Layer**: Manages the state of the remote (current TV, connection status) and routes commands.
3.  **Communication Layer**:
    *   **Roku ECP**: HTTP-based control for Roku TVs.
    *   **Generic HTTP/TCP**: For other smart TVs.
    *   **IR Bridge**: API to talk to an external ESP32 IR Blaster.
4.  **Discovery Layer**: Background service using **SSDP/mDNS (zeroconf)** to find devices.

## 2. Directory Structure

```text
Project remote/
├── implementation_plan.md
├── requirements.txt
├── Remote.py                # Main Entry Point (Kivy App)
├── config.py                # Configuration and Constants
├── assets/                  # Icons/Images (if any)
└── modules/
    ├── __init__.py
    ├── discovery.py         # Network Discovery (SSDP/Roku)
    ├── remote_base.py       # Abstract Base Class for Remotes
    ├── roku_controller.py   # Roku ECP Implementation
    ├── ir_controller.py     # IR Blaster Implementation
    └── storage.py           # Device persistence (JSON)
```

## 3. Technology Stack

*   **Language**: Python 3.x
*   **UI Framework**: Kivy (Cross-platform for Android/Windows)
*   **Networking**: `requests` (HTTP), `socket` (UDP/TCP), `zeroconf` (Discovery)
*   **Async**: `kivy.clock` or `threading` to keep UI responsive.

## 4. Implementation Steps

### Step 1: Core Definitions & Configuration
*   Define the `RemoteDevice` data class.
*   Setup `requirements.txt`.

### Step 2: Network Discovery
*   Implement SSDP discovery logic to find Roku devices (Target: `roku:ecp`).
*   Implement generic port scanning or specific mDNS for other TCL models.

### Step 3: Roku Control Module
*   Implement `RokuController` class.
*   Methods: `send_key(key)`, `launch_app(app_id)`, `query_device()`.

### Step 4: IR & Fallback
*   Implement `IRController` to send HTTP requests to a hypothetical ESP32 endpoint (e.g., `http://esp32-ip/ir?code=...`).

### Step 5: Kivy UI Implementation
*   Design a modern dark-themed UI.
*   **Main Screen**: D-Pad, Volume, Playback, Source.
*   **Discovery Screen**: List found devices.
*   **Settings**: Configure IR blaster IP.

### Step 6: Integration in `Remote.py`
*   Tie the UI events to the controller logic.
*   Handle connection states and error feedback.

## 5. Deployment
*   The code will be runnable on Windows immediately.
*   For Android, `buildozer` would be used (instructions included in documentation).
