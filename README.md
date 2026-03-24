# 🔧 IoT-Based Predictive Maintenance System for Industrial Machines

<p align="center">
  <img src="https://img.shields.io/badge/Platform-ESP32%20%7C%20Arduino%20Uno-blue?style=for-the-badge&logo=arduino"/>
  <img src="https://img.shields.io/badge/Cloud-ThingSpeak-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Backend-Flask%20%2B%20SocketIO-red?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/Mobile-Android%20Studio-3DDC84?style=for-the-badge&logo=android"/>
  <img src="https://img.shields.io/badge/Language-Embedded%20C%20%7C%20Python-yellow?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge"/>
</p>

<p align="center">
  <b>Best Project Award – Final Year Engineering Exhibition, Goa College of Engineering, 2025</b><br/>
  Real-time IoT system that monitors industrial machines using multi-sensor fusion, cloud analytics, and threshold-based alerting to predict failures before they occur.
</p>

---

## 📌 Table of Contents
- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Hardware Components](#-hardware-components)
- [Software Stack](#-software-stack)
- [Features](#-features)
- [Circuit Design](#-circuit-design)
- [Results & Performance](#-results--performance)
- [Installation & Setup](#-installation--setup)
- [Project Structure](#-project-structure)
- [Future Work](#-future-work)
- [Team](#-team)

---

## 🧠 Overview

Traditional industrial maintenance relies on scheduled servicing or reactive repair, both of which are inefficient — either over-servicing or failing to catch early signs of failure. This project implements a **Predictive Maintenance System** that continuously monitors machine health parameters in real time using IoT sensors, performs threshold-based anomaly detection, and delivers instant alerts to operators via mobile and cloud platforms.

The system is designed to align with **Industry 4.0** goals — scalable, cost-effective, connected, and data-driven.

**Key Outcomes:**
- ~30% reduction in anticipated machine downtime through early fault detection
- ~95% data reliability in real-time sensor monitoring
- ~40% improvement in maintenance response efficiency via cloud dashboard
- ~35% reduction in anomaly response time through automated alerts

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SENSOR LAYER                             │
│  ADXL345 (Vibration) │ DHT11 (Temp/Humidity) │ RTD │ ACS712   │
└─────────────┬───────────────────┬─────────────────────┬────────┘
              │                   │                     │
       ┌──────▼──────┐    ┌───────▼──────┐    ┌────────▼───────┐
       │    ESP32    │    │  Arduino Uno  │    │ PID Controller │
       │  (Wi-Fi +   │◄───│  (Analog ADC  │    │  (i-Therm)    │
       │   Digital)  │    │   Processing) │    │  RTD Feedback  │
       └──────┬──────┘    └───────────────┘    └────────────────┘
              │
     ┌────────┼────────────┐
     │        │            │
┌────▼───┐ ┌──▼───────┐ ┌──▼──────────┐
│Buzzer  │ │ LED Dome  │ │ 16x2 LCD   │
│(Audible│ │ (Visual   │ │ (Local     │
│ Alert) │ │  Alert)   │ │  Display)  │
└────────┘ └──────────┘ └────────────┘
              │
       HTTP POST (Wi-Fi)
              │
    ┌─────────▼─────────────┐
    │   Flask Server        │
    │   + SocketIO          │
    │   (Python Backend)    │
    └─────────┬─────────────┘
              │
    ┌─────────┴──────────────┐
    │                        │
┌───▼──────────┐    ┌────────▼────────┐
│  ThingSpeak  │    │  Android App    │
│  Cloud       │    │  (Real-time     │
│  Dashboard   │    │   Alerts + Data)│
└──────────────┘    └─────────────────┘
```

---

## 🔩 Hardware Components

| Component | Model | Role | Interface |
|-----------|-------|------|-----------|
| Microcontroller (Main) | **ESP32** | Wi-Fi transmission, cloud connectivity, digital sensor processing, alert logic | Wi-Fi, I2C, GPIO |
| Microcontroller (Secondary) | **Arduino Uno (ATmega328P)** | Analog signal processing, current sensing, LCD display | Analog ADC, I2C |
| Vibration Sensor | **ADXL345 Accelerometer** | 3-axis vibration monitoring (±2g to ±16g range) | I2C (SDA/SCL) |
| Temperature & Humidity | **DHT11** | Ambient temperature (0–50°C ±2°C) and humidity (20–90% RH ±5%) | Single-wire digital |
| Precision Temperature | **RTD (PT100)** | High-accuracy surface temperature of motor/winding (-50°C to 500°C) | Instrumentation amplifier → Arduino ADC |
| Current Sensor | **ACS712 (20A variant)** | Hall-effect based AC/DC current monitoring for 1-phase and 3-phase machines | Analog → Arduino ADC |
| Temperature Controller | **PID Controller (i-Therm)** | Autonomous thermal regulation using RTD feedback (PV vs SV comparison) | Relay/SSR output |
| Display | **16×2 LCD (HD44780)** | Local real-time display of temperature, vibration, and current values | I2C module |
| Visual Alert | **LED Dome Indicator (Red)** | High-visibility local alarm when 90% threshold is crossed | Digital GPIO |
| Audible Alert | **Active Buzzer (5V)** | Audible warning in noisy industrial environments | Digital GPIO |
| Enclosure | **Custom Acrylic Box (30×30×30 cm)** | Laser-cut transparent housing with ventilation, LCD and PID front-panel mounting | — |

### Sensor Threshold Logic

| Sensor | Normal Range | Alert Trigger (90%) | Critical Action |
|--------|-------------|---------------------|-----------------|
| RTD Temperature | Below set threshold | Alert + Log to cloud + Notify app | PID activates cooling, critical alert |
| ADXL345 Vibration | ±0.12g (idle) – ±1.8g (load) | App alert for mechanical inspection + cloud log | Buzzer + LED, recommend shutdown |
| ACS712 Current | 0–8A typical | Overcurrent flag + app notification | Alert + log event |
| DHT11 Temp | 0–40°C ambient | Warning if combined with high surface temp | Log humidity + temp |

---

## 💻 Software Stack

### Embedded Firmware (ESP32 & Arduino Uno)
- **Language:** Embedded C / Arduino IDE (v1.8.1)
- **Libraries:** `WiFi.h`, `HTTPClient.h`, `DHT.h`, `Wire.h`, `Adafruit_Sensor.h`, `Adafruit_ADXL345_U.h`
- **Logic:** Continuous sensor polling → threshold comparison → HTTP POST to Flask server → local alert triggers
- **Update Rate:** Sensor data transmitted every 15 seconds; average cloud transmission delay < 1.8 seconds
- **Wi-Fi Range Tested:** Up to 60 meters (indoor, controlled environment)
- **Power:** ESP32 at 3.3V (~0.5W); Arduino Uno at 5V

### Python Flask Backend
- **Framework:** Flask + Flask-SocketIO
- **Key Libraries:** `matplotlib`, `numpy`, `pytz`, `datetime`, `base64`, `io`
- **Endpoints:**
  - `POST /data` — Receives JSON sensor payload from ESP32, stores rolling 20-point buffer, generates plots, emits via SocketIO
  - `GET /command` — Returns command JSON to ESP32 (e.g., `{"action": "toggle_led"}`)
  - `GET /` — Renders real-time HTML dashboard
- **Real-time:** SocketIO `emit('new_data', {...})` pushes base64-encoded matplotlib plots to browser without page refresh
- **Timezone:** Asia/Kolkata (IST) for timestamps

### Web Dashboard (HTML + JavaScript)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Real-time updates:** Socket.IO client (`socket.on('new_data', ...)`) updates plot images and timestamp every second
- **Plots:** Plot 1 — Temperature & Humidity vs Time; Plot 2 — X/Y/Z Vibration Axis vs Time
- **Responsive:** Flexbox layout with media query breakpoints at 768px

### Cloud Platform
- **ThingSpeak:** Multi-channel data logging at 15-second intervals; live charts and historical trend visualization accessible remotely

### Android Mobile App
- **Built with:** Android Studio
- **Connectivity:** HTTP-based cloud sync (primary) + Bluetooth (fallback)
- **Features:** Live sensor dashboard, threshold breach notifications, alert acknowledgment, historical trend viewing

---

## ✨ Features

- **Real-Time Multi-Parameter Monitoring** — Simultaneous tracking of vibration (3-axis), surface temperature (RTD), ambient conditions (DHT11), and electrical current (ACS712)
- **90% Threshold Alert System** — Proactive alerts triggered before critical limits are reached, giving maintenance teams time to act
- **Dual Alert Mechanism** — Local (LED dome + buzzer + LCD) AND remote (Android push notification + ThingSpeak log)
- **PID Temperature Control** — Autonomous closed-loop thermal regulation with ±2°C stability; PID adjusts cooling/heating without microcontroller intervention
- **Cloud Analytics** — ThingSpeak dashboard with real-time plots, timestamped logs, and historical trend analysis
- **Wi-Fi + Bluetooth Redundancy** — Falls back to Bluetooth if internet connectivity is unavailable
- **Dual-Mode Operation:**
  - **Manual Mode:** User monitors and acknowledges alerts via app; remote start/stop control
  - **Automated Mode:** Fully autonomous threshold detection, alerting, and cloud logging
- **Modular & Scalable Architecture** — Each sensor module is independently replaceable; supports both single-phase and three-phase machine monitoring
- **3D Modeled Enclosure** — Designed in Autodesk Fusion 360; acrylic housing with front-panel PID display, LCD, and indicator light

---

## ⚡ Circuit Design

### Circuit 1 — ESP32 + ADXL345 + DHT11
- ADXL345 → ESP32 via I2C (GPIO 21 = SDA, GPIO 22 = SCL), powered at 3.3V
- DHT11 → ESP32 via single-wire digital protocol (GPIO 27)
- ESP32 compares values against 90% threshold → HTTP POST to Flask → ThingSpeak + Android app

### Circuit 2 — Arduino Uno + ACS712 (3-Phase Current Sensing)
- Three ACS712 sensors (one per phase: U, V, W) → Analog pins A0, A1, A2 on Arduino Uno
- Arduino calculates actual current values → shares data with ESP32 for consolidated alerting
- LCD display driven from Arduino via I2C

### Circuit 3 — PID Controller + RTD (Thermal Management)
- RTD → Signal conditioning/instrumentation amplifier → PID controller (i-Therm)
- PID compares measured temperature (PV) with setpoint (SV)
- On deviation → relay/SSR output activates cooling/heating mechanism
- Operates autonomously — offloads thermal control from microcontroller

---

## 📊 Results & Performance

### Sensor Test Results

| Test Case | Temperature (°C) | Vibration (g) | Current (A) | Status | System Response |
|-----------|:-:|:-:|:-:|:-:|---|
| Normal Operation | 40 | 0.35 | 1.8 | ✅ Normal | No action |
| High Temp Load | 74 | 0.42 | 2.0 | ⚠️ Warning | PID activates, alert sent |
| Excessive Vibration | 45 | 1.10 | 1.6 | 🔴 Critical | Buzzer ON, app notification |
| Overcurrent Spike | 42 | 0.50 | 2.8 | 🔴 Critical | Alert + cloud log |
| Safe Idle | 33 | 0.12 | 0.5 | ✅ Normal | No action |

### Quantitative Performance Metrics

| Metric | Value |
|--------|-------|
| RTD Temperature Range Tested | Up to 72°C (PID held within ±2°C of setpoint) |
| Vibration Baseline (Idle) | ±0.12g |
| Vibration at Max Load | ±1.8g (threshold alert: ±2g) |
| Max Current Under Full Load | 8.7A |
| Wi-Fi Transmission Range | ~60 meters (indoor) |
| Cloud Update Interval | 15 seconds |
| Average Cloud Transmission Delay | < 1.8 seconds |
| ESP32 Power Consumption | ~0.5W at 3.3V |
| DHT11 Temperature Accuracy | ±2°C |
| DHT11 Humidity Accuracy | ±5% RH |
| Data Reliability | ~95% (continuous real-time tracking) |

---

## 🚀 Installation & Setup

### Prerequisites
- Arduino IDE v1.8.1+
- Python 3.8+
- Android Studio (for app)
- ThingSpeak account (free)

### 1. ESP32 Firmware
```bash
# Install required Arduino libraries via Library Manager:
# - Adafruit ADXL345
# - Adafruit Unified Sensor
# - DHT sensor library
# - ESP32 board package

# In esp32_firmware/config.h, set:
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* server   = "http://YOUR_SERVER_IP:5000";
```
Upload `esp32_firmware/main.ino` to ESP32 via Arduino IDE.

### 2. Arduino Uno Firmware
Upload `arduino_firmware/current_sensor.ino` to Arduino Uno via Arduino IDE.

### 3. Python Flask Backend
```bash
pip install flask flask-socketio matplotlib numpy pytz

# Run the server
python app.py
# Server starts on http://0.0.0.0:5000
```

### 4. ThingSpeak Setup
- Create a ThingSpeak channel with 5 fields: Temperature, Humidity, X-Axis, Y-Axis, Z-Axis
- Update the ThingSpeak API key in the ESP32 firmware

### 5. Access Dashboard
- Open browser: `http://<server-ip>:5000`
- Connect Android app to same Wi-Fi network and point to ESP32 IP

---

## 📁 Project Structure

```
predictive-maintenance-iot/
│
├── esp32_firmware/
│   ├── main.ino               # ESP32 main loop: sensor reading, Wi-Fi, HTTP POST
│   ├── config.h               # Wi-Fi credentials, server address, pin definitions
│   └── threshold_logic.ino    # 90% threshold checks, alert triggers
│
├── arduino_firmware/
│   ├── current_sensor.ino     # ACS712 current reading + LCD display
│   └── rtd_pid.ino            # RTD analog read, serial output to ESP32
│
├── flask_server/
│   ├── app.py                 # Flask + SocketIO server, /data endpoint, plot generation
│   └── templates/
│       └── index.html         # Real-time dashboard (Socket.IO, CSS, JS)
│
├── android_app/               # Android Studio project
│   └── ...
│
├── hardware/
│   ├── circuit_diagrams/      # ESP32+sensors, Arduino+ACS712, PID+RTD circuit diagrams
│   ├── 3d_model/              # Autodesk Fusion 360 enclosure files
│   └── bom.csv                # Bill of Materials with component costs
│
├── docs/
│   ├── project_report.pdf     # Full technical report (GCE, 2025)
│   └── block_diagram.png      # System architecture diagram
│
└── README.md
```

---

## 🔮 Future Work

- **ML-based Anomaly Detection** — Replace static thresholds with trained models (LSTM/Isolation Forest) for dynamic pattern recognition and reduced false positives
- **Edge Computing** — Deploy inference on Raspberry Pi / Jetson Nano to reduce cloud dependency and improve real-time response
- **Expanded Sensor Suite** — Add acoustic emission sensors, pressure sensors, and thermal cameras for deeper diagnostics
- **5G IoT Integration** — Enable faster, lower-latency remote monitoring in large industrial deployments
- **Auto-calibration** — Self-calibrating sensor routines to compensate for drift over time
- **CMMS Integration** — Connect with SAP or CMMS platforms for automated work order generation and spare parts management
- **Fleet Monitoring** — Multi-node ESP32 mesh for factory-wide machine monitoring from a single dashboard
- **Solar Power Module** — Energy harvesting from machine vibrations for off-grid deployments

---

## 👥 Team

| Name | PR Number |
|------|-----------|
| Brian Dias | 202111941 |
| Sheshank Shrikant Naik | 202111792 |
| Steve Alfredo Christy Bernard | 202111777 |
| Valois Ian Fernandes | 202111872 |

**Guide:** Prof. Nilesh Borkar, Associate Professor, Dept. of Electrical & Electronics Engineering, Goa College of Engineering

**Institution:** Goa College of Engineering, Farmagudi, Goa — Department of Electrical & Electronics Engineering (2024–2025)

---

## 🏆 Recognition

> **Best Project Award** — Final Year Engineering Exhibition, GCE 2025  
> Recognized for innovation in AI-driven Predictive Maintenance for Industry 4.0 applications.

---

## 📄 License

This project is submitted in partial fulfillment of the requirements for the degree of **Bachelor of Engineering in Electrical and Electronics Engineering**, Goa University (2025).

---

<p align="center">
  Built with ❤️ at Goa College of Engineering | Industry 4.0 | IoT | Embedded Systems | Cloud Analytics
</p>
