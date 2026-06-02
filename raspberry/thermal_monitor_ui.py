import time
import os
import sys
import json
import board
import busio
import numpy as np
import cv2
import serial
import RPi.GPIO as GPIO
from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import requests

# =====================================================
# CONFIG FILE HANDLING
# =====================================================
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "threshold": 30.0,
    "phone_number": "+639XXXXXXXXX",
    "message": "Alert! Temperature threshold exceeded.",
    "sms_enabled": True,
    "buzzer_enabled": True,
    "sensor_interval": 2,
    "api_url": ""
}

def load_config():
    """Load configuration from file or create default one."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

# =====================================================
# HARDWARE SETUP
# =====================================================
BUZZER_PIN = 17
LOG_FILE = "thermal_log.txt"
SIM900_PORT = "/dev/serial0"
SIM900_BAUD = 9600

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

# =====================================================
# LOG VIEWER (Terminal-like Output)
# =====================================================
root = tk.Tk()
root.title("Thermal Camera Configuration")
root.geometry("500x600")

# Text widget for terminal output
log_text = tk.Text(root, height=10, bg="black", fg="lime", insertbackground="white")
log_text.pack(fill="both", expand=False, padx=10, pady=10)

def log_event(message):
    """Append timestamped events to log file and UI."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)

    log_text.insert(tk.END, line)
    log_text.see(tk.END)
    print(line.strip())

# =====================================================
# DETECT HARDWARE
# =====================================================
sensor = None
try:
    import adafruit_amg88xx
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_amg88xx.AMG88XX(i2c)
    log_event("AMG8833 detected.")
except Exception:
    log_event("AMG8833 not detected, simulation mode.")

gsm = None
if config["sms_enabled"]:
    try:
        gsm = serial.Serial(SIM900_PORT, SIM900_BAUD, timeout=1)
        time.sleep(1)
        gsm.write(b'AT\r')
        time.sleep(0.5)
        resp = gsm.read_all().decode(errors='ignore')
        if "OK" in resp:
            log_event("SIM900 GSM ready.")
        else:
            log_event("SIM900 not responding properly.")
    except Exception as e:
        log_event(f"SIM900 not responding: {e}")

# =====================================================
# UTILITIES
# =====================================================
def send_sms(message):
    """Send SMS via SIM900."""
    if gsm is None:
        log_event("GSM unavailable. SMS not sent.")
        return
    try:
        gsm.write(b'AT+CMGF=1\r')
        time.sleep(0.5)
        gsm.write(f'AT+CMGS="{config["phone_number"]}"\r'.encode())
        time.sleep(0.5)
        gsm.write(message.encode() + b"\x1A")
        log_event(f"SMS sent to {config['phone_number']}: {message}")
    except Exception as e:
        log_event(f"SMS failed: {e}")

def buzzer_alert(duration=2):
    """Activate buzzer if enabled."""
    if not config["buzzer_enabled"]:
        return
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def get_temperature_data():
    """Read from AMG8833 or simulate."""
    if sensor:
        try:
            pixels = np.array(sensor.pixels, dtype=np.float32)
            return pixels
        except Exception:
            log_event("Sensor read failed, simulating data.")
    return np.random.uniform(25.0, 35.0, (8, 8))

def send_api_data(temp):
    """Send temperature data to web API."""
    try:
        payload = {"temp": temp}
        if config["api_url"]:
            res = requests.post(config["api_url"], json=payload)
            if res.status_code == 200:
                log_event("API payload sent successfully.")
            else:
                log_event(f"API returned {res.status_code}")
    except Exception as e:
        log_event(f"API error: {e}")

# =====================================================
# MAIN LOOP (runs in thread)
# =====================================================
running = False

def monitor_loop():
    global running
    log_event("🚀 Thermal monitor started")
    alert_triggered = False

    while running:
        pixels = get_temperature_data()
        max_temp = pixels.max()

        normalized = cv2.normalize(pixels, None, 0, 255, cv2.NORM_MINMAX)
        frame = np.uint8(normalized)
        frame_big = cv2.resize(frame, (240, 240), interpolation=cv2.INTER_CUBIC)
        frame_color = cv2.applyColorMap(frame_big, cv2.COLORMAP_INFERNO)
        cv2.putText(frame_color, f"Max: {max_temp:.2f}C", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow("Thermal Camera", frame_color)
        log_event(f"Max Temp: {max_temp:.2f}°C")
        print(max_temp, config["threshold"])
        if max_temp > config["threshold"]:
            print(max_temp, "trigger alerts")
            # if not alert_triggered:
            log_event("🔥 Alert! Threshold exceeded.")
            buzzer_alert(1)
            send_sms(f"Alert! Temperature reached {max_temp:.2f}°C")
            send_api_data(max_temp)
            time.sleep(2)
        else:
            alert_triggered = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

        time.sleep(config["sensor_interval"])

    log_event("🛑 Monitor stopped.")
    cv2.destroyAllWindows()
    GPIO.output(BUZZER_PIN, GPIO.LOW)

# =====================================================
# UI SECTION
# =====================================================
def start_monitor():
    global running
    if running:
        messagebox.showinfo("Info", "Monitor already running.")
        return
    running = True
    threading.Thread(target=monitor_loop, daemon=True).start()
    log_event("Monitor thread started.")

def stop_monitor():
    global running
    running = False
    log_event("Monitor stopped by user.")

def save_settings():
    config["threshold"] = float(threshold_var.get())
    config["phone_number"] = phone_var.get()
    config["message"] = message_var.get()
    config["sms_enabled"] = sms_var.get()
    config["buzzer_enabled"] = buzzer_var.get()
    config["api_url"] = api_var.get()
    save_config(config)
    messagebox.showinfo("Saved", "Configuration saved successfully!")
    log_event("Configuration updated.")

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

threshold_var = tk.DoubleVar(value=config["threshold"])
phone_var = tk.StringVar(value=config["phone_number"])
message_var = tk.StringVar(value=config["message"])
api_var = tk.StringVar(value=config["api_url"])
sms_var = tk.BooleanVar(value=config["sms_enabled"])
buzzer_var = tk.BooleanVar(value=config["buzzer_enabled"])

ttk.Label(frame, text="Temperature Threshold (°C):").pack(anchor="w")
ttk.Entry(frame, textvariable=threshold_var).pack(fill="x")

ttk.Label(frame, text="Phone Number:").pack(anchor="w", pady=(10, 0))
ttk.Entry(frame, textvariable=phone_var).pack(fill="x")

ttk.Label(frame, text="SMS Message:").pack(anchor="w", pady=(10, 0))
ttk.Entry(frame, textvariable=message_var).pack(fill="x")

ttk.Label(frame, text="API URL (optional):").pack(anchor="w", pady=(10, 0))
ttk.Entry(frame, textvariable=api_var).pack(fill="x")

ttk.Checkbutton(frame, text="Enable SMS", variable=sms_var).pack(anchor="w", pady=(10, 0))
ttk.Checkbutton(frame, text="Enable Buzzer", variable=buzzer_var).pack(anchor="w")

ttk.Button(frame, text="Save Configuration", command=save_settings).pack(fill="x", pady=10)
ttk.Button(frame, text="Start Monitor", command=start_monitor).pack(fill="x", pady=5)
ttk.Button(frame, text="Stop Monitor", command=stop_monitor).pack(fill="x", pady=5)

ttk.Label(frame, text="Press 'q' in camera window to close.").pack(pady=10)

root.mainloop()
