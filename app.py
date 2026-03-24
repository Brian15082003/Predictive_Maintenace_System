"""
Flask Server for IoT Predictive Maintenance System
Real-Time Sensor Data Visualization and Command Control

Authors: Brian Dias, Sheshank Naik, Steve Bernard, Valois Fernandes
Institution: Goa College of Engineering, 2024-2025
"""

import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import pytz

# ── App Initialization ──────────────────────────────────────────
app = Flask(__name__)
socketio = SocketIO(app)

# Timezone
IST = pytz.timezone('Asia/Kolkata')

# Rolling data storage (last 20 readings)
MAX_DATA_POINTS = 20
real_time_data = {
    'timestamps':  [],
    'temperature': [],
    'humidity':    [],
    'x_axis':      [],
    'y_axis':      [],
    'z_axis':      [],
    'current':     []
}

# Alert thresholds (90% of safe operating limits)
THRESHOLDS = {
    'temperature': 63,    # 90% of 70°C safe limit
    'vibration':   1.8,   # 90% of ±2g safe limit
    'current':     8.0,   # 90% of ~8.7A max
    'humidity':    81     # 90% of 90% RH max
}


# ── Helper: Generate Real-Time Plots ────────────────────────────
def create_real_time_plots():
    timestamps  = real_time_data['timestamps']
    temperature = real_time_data['temperature']
    humidity    = real_time_data['humidity']
    x_axis      = real_time_data['x_axis']
    y_axis      = real_time_data['y_axis']
    z_axis      = real_time_data['z_axis']

    # Plot 1: Temperature and Humidity vs Time
    plt.figure(figsize=(6, 4))
    plt.plot(timestamps, temperature, label='Temperature (°C)', color='r', marker='o')
    plt.plot(timestamps, humidity,    label='Humidity (%)',      color='y', marker='o')
    plt.axhline(y=THRESHOLDS['temperature'], color='r', linestyle='--', alpha=0.5, label='Temp Threshold')
    plt.xlabel('Time (IST)')
    plt.ylabel('Temperature (°C) / Humidity (%)')
    plt.title('Real-Time Temperature and Humidity')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    plot1_bytes = io.BytesIO()
    plt.savefig(plot1_bytes, format='png')
    plot1_bytes.seek(0)
    plot1_base64 = base64.b64encode(plot1_bytes.getvalue()).decode('utf-8')
    plt.close()

    # Plot 2: X, Y, Z Axis Vibration vs Time
    plt.figure(figsize=(6, 4))
    plt.plot(timestamps, x_axis, label='X Axis', color='r', marker='o')
    plt.plot(timestamps, y_axis, label='Y Axis', color='g', marker='o')
    plt.plot(timestamps, z_axis, label='Z Axis', color='b', marker='o')
    plt.axhline(y=THRESHOLDS['vibration'],  color='orange', linestyle='--', alpha=0.5, label='Vibration Threshold')
    plt.axhline(y=-THRESHOLDS['vibration'], color='orange', linestyle='--', alpha=0.5)
    plt.xlabel('Time (IST)')
    plt.ylabel('Axis Readings (g)')
    plt.title('Real-Time X, Y, Z Axis Vibration')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    plot2_bytes = io.BytesIO()
    plt.savefig(plot2_bytes, format='png')
    plot2_bytes.seek(0)
    plot2_base64 = base64.b64encode(plot2_bytes.getvalue()).decode('utf-8')
    plt.close()

    return plot1_base64, plot2_base64


# ── Helper: Check Thresholds ────────────────────────────────────
def check_thresholds(data):
    alerts = []
    if data.get('temperature') and data['temperature'] >= THRESHOLDS['temperature']:
        alerts.append({'type': 'TEMPERATURE', 'value': data['temperature'], 'threshold': THRESHOLDS['temperature']})
    if data.get('x_axis') and abs(data['x_axis']) >= THRESHOLDS['vibration']:
        alerts.append({'type': 'VIBRATION_X', 'value': data['x_axis'], 'threshold': THRESHOLDS['vibration']})
    if data.get('y_axis') and abs(data['y_axis']) >= THRESHOLDS['vibration']:
        alerts.append({'type': 'VIBRATION_Y', 'value': data['y_axis'], 'threshold': THRESHOLDS['vibration']})
    if data.get('current') and data['current'] >= THRESHOLDS['current']:
        alerts.append({'type': 'CURRENT', 'value': data['current'], 'threshold': THRESHOLDS['current']})
    return alerts


# ── Routes ───────────────────────────────────────────────────────

@app.route('/')
def index():
    """Render the real-time monitoring dashboard."""
    return render_template('index.html')


@app.route('/data', methods=['POST'])
def receive_data():
    """
    Receive sensor data from ESP32 via HTTP POST.
    Expected JSON payload:
    {
        "temperature": 42.5,
        "humidity": 65.0,
        "X axis": 0.35,
        "Y axis": 0.12,
        "Z axis": 0.08,
        "current": 2.1
    }
    """
    data = request.get_json()

    if data:
        temperature = data.get('temperature')
        humidity    = data.get('humidity')
        x_axis      = data.get('X axis')
        y_axis      = data.get('Y axis')
        z_axis      = data.get('Z axis')
        current     = data.get('current', 0)

        # Record IST timestamp
        current_time = datetime.now(IST).strftime('%H:%M:%S')

        # Append to rolling buffer
        real_time_data['timestamps'].append(current_time)
        for key, value in zip(
            ['temperature', 'humidity', 'x_axis', 'y_axis', 'z_axis', 'current'],
            [temperature, humidity, x_axis, y_axis, z_axis, current]
        ):
            real_time_data[key].append(value)

        # Trim to MAX_DATA_POINTS
        if len(real_time_data['timestamps']) > MAX_DATA_POINTS:
            for key in real_time_data.keys():
                real_time_data[key].pop(0)

        # Check alert thresholds
        alerts = check_thresholds(data)

        # Generate updated plots
        plot1_image, plot2_image = create_real_time_plots()

        # Emit real-time update to all connected clients
        socketio.emit('new_data', {
            'plot1_image': plot1_image,
            'plot2_image': plot2_image,
            'alerts': alerts,
            'latest': {
                'time':        current_time,
                'temperature': temperature,
                'humidity':    humidity,
                'x_axis':      x_axis,
                'y_axis':      y_axis,
                'z_axis':      z_axis,
                'current':     current
            }
        })

        print(f"[{current_time}] Temp: {temperature}°C | Humidity: {humidity}% | "
              f"X: {x_axis} | Y: {y_axis} | Z: {z_axis} | Current: {current}A")

        if alerts:
            print(f"  ⚠️  ALERTS: {alerts}")

        return jsonify({"message": "Data received successfully", "alerts": alerts}), 200
    else:
        return jsonify({"error": "Invalid JSON data"}), 400


@app.route('/command', methods=['GET'])
def send_command():
    """
    Send control commands to ESP32.
    ESP32 polls this endpoint to receive commands.
    """
    command = {"action": "toggle_led"}
    return jsonify(command)


@app.route('/status', methods=['GET'])
def system_status():
    """Return current system status and latest sensor readings."""
    if not real_time_data['timestamps']:
        return jsonify({"status": "No data received yet"}), 200

    latest_idx = -1
    return jsonify({
        "status":      "online",
        "last_update": real_time_data['timestamps'][latest_idx],
        "temperature": real_time_data['temperature'][latest_idx],
        "humidity":    real_time_data['humidity'][latest_idx],
        "x_axis":      real_time_data['x_axis'][latest_idx],
        "y_axis":      real_time_data['y_axis'][latest_idx],
        "z_axis":      real_time_data['z_axis'][latest_idx],
        "thresholds":  THRESHOLDS
    })


@app.route('/history', methods=['GET'])
def get_history():
    """Return historical data buffer for all parameters."""
    return jsonify(real_time_data)


# ── Run ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("🔧 Predictive Maintenance System - Flask Server")
    print("   Listening on http://0.0.0.0:5000")
    print("   Dashboard: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
