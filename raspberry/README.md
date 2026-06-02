# Raspberry Pi Thermal Monitor Client

This directory contains the Raspberry Pi client for the Chick Fever Detection System. It reads temperatures from an **Adafruit AMG8833** thermal camera and sends alerts to the Django dashboard.

---

## Hardware Requirements

- Raspberry Pi (any model with GPIO, I2C, and serial)
- Adafruit AMG8833 8x8 IR thermal camera (I2C)
- Active buzzer (optional, GPIO 17)
- SIM900 GSM module (optional, serial UART)

---

## Installation

Requires **Python 3.12+**.

Run these commands **on the Raspberry Pi**:

```bash
cd chick-thermo-system/raspberry
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `adafruit-circuitpython-amg88xx` — AMG8833 sensor driver
- `opencv-python` — Thermal camera visualization
- `RPi.GPIO` — Buzzer control
- `pyserial` — SIM900 GSM communication
- `requests` — HTTP calls to the Django API

---

## Usage

```bash
python thermal_monitor_ui.py
```

A Tkinter window will open allowing you to configure settings. Press **Start Monitor** to begin reading the thermal camera.

---

## Configuration

Automatically saved to `raspberry/config.json` on first run:

| Setting | Default | Description |
|---------|---------|-------------|
| `threshold` | `30.0` | Temperature threshold in Celsius |
| `phone_number` | `+639XXXXXXXXX` | SMS recipient number |
| `message` | `Alert!` | SMS message body |
| `sms_enabled` | `true` | Toggle SMS alerts |
| `buzzer_enabled` | `true` | Toggle buzzer alerts |
| `api_url` | `""` | Django API URL (e.g. `http://192.168.1.100:8000/api/monitor/`) |

---

## Hardware Wiring

| Pin | Component | Connection |
|-----|-----------|------------|
| GPIO 2 (SDA) | AMG8833 | I2C Data |
| GPIO 3 (SCL) | AMG8833 | I2C Clock |
| GPIO 17 | Buzzer | Signal (+) |
| TX / RX | SIM900 | UART Serial (`/dev/serial0`) |

**Enable I2C:** `sudo raspi-config` → Interface Options → I2C → Enable

---

## Simulation Mode

If the AMG8833 sensor is not detected, randomized temperature data is used automatically. This allows testing the full alert pipeline (buzzer, SMS, API) without physical hardware.

---

## Logs

Events are written to `raspberry/thermal_log.txt` and displayed in the Tkinter terminal window.
