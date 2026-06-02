# Chick Fever Detection Dashboard

A real-time fever monitoring system for chicks using thermal imaging. A **Raspberry Pi** equipped with an AMG8833 thermal camera reads chick temperatures and sends data to a **Django dashboard** that displays live alerts, tracks fever history, and supports SMS/buzzer notifications.

---

## Features

- **Real-time Dashboard** — Live active alerts auto-refresh every 2 seconds via HTMX
- **Fever Detection** — Alerts automatically created when temperature >= 39.5 C
- **Thermal Camera Feed** — OpenCV-based visualizer with color mapping and max temperature overlay
- **Buzzer Alert** — GPIO-connected buzzer sounds on threshold exceed (Raspberry Pi side)
- **SMS Notifications** — SIM900 GSM module sends SMS alerts when fever is detected
- **REST API** — DRF endpoint for the Pi client to push temperature data
- **Alert Management** — Resolve alerts, paginated history, active/unresolved counts
- **API Documentation** — Auto-generated Swagger UI and ReDoc
- **Simulation Mode** — Works without hardware using randomized temperature data

---

## Architecture

```
┌─────────────────────────┐     POST /api/monitor/     ┌────────────────────────────┐
│  Raspberry Pi (Client)  │ ──────────────────────────> │  Django Server (Dashboard) │
│                         │    { "temp": 40.2 }         │                            │
│  ┌───────────────────┐  │                             │  ┌──────────────────────┐  │
│  │  AMG8833 Thermal  │  │                             │  │  SQLite Database     │  │
│  │  Camera (I2C)     │  │                             │  │  ┌ Chick             │  │
│  └────────┬──────────┘  │                             │  │  ├ TemperatureReading │  │
│           │              │                             │  │  └ FeverAlert        │  │
│  ┌────────┴──────────┐  │                             │  └──────────────────────┘  │
│  │  OpenCV Visualizer│  │                             │                            │
│  └───────────────────┘  │                             │  ┌──────────────────────┐  │
│                         │                             │  │  HTMX Dashboard      │  │
│  ┌───────────────────┐  │                             │  │  (auto-refresh 2s)   │  │
│  │  SIM900 GSM Module│  │                             │  └──────────────────────┘  │
│  │  (Serial)          │  │                             │                            │
│  └───────────────────┘  │                             │  ┌──────────────────────┐  │
│                         │                             │  │  Swagger / ReDoc     │  │
│  ┌───────────────────┐  │                             │  └──────────────────────┘  │
│  │  Buzzer (GPIO 17) │  │                             └────────────────────────────┘
│  └───────────────────┘  │
└─────────────────────────┘
```

---

## Hardware Requirements

| Component | Purpose |
|-----------|---------|
| Raspberry Pi (any model with GPIO) | Runs the thermal monitor client |
| Adafruit AMG8833 (8x8 IR thermal camera) | Reads temperature grid via I2C |
| SIM900 GSM module (optional) | Sends SMS alerts via serial |
| Active buzzer (optional) | Audible alert via GPIO pin 17 |
| Jumper wires | I2C and GPIO connections |

---

## Quick Start — Django Server

```bash
# 1. Clone and enter the project
cd chick-thermo-system

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate    # Linux/macOS
# venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. (Optional) Seed fake data for testing
python manage.py generate_fake_data

# 7. Run the development server
python manage.py runserver
```

Visit **http://localhost:8000** — login with your superuser credentials.

---

## Quick Start — Raspberry Pi Client

```bash
# On your Raspberry Pi
cd chick-thermo-system/raspberry

# Install hardware dependencies
pip install -r requirements.txt

# Run the thermal monitor UI
python thermal_monitor_ui.py
```

A Tkinter window opens where you can configure the threshold, phone number, API URL, and toggle SMS/buzzer. Press **Start Monitor** to begin reading from the AMG8833 (or simulated data if no sensor is detected).

---

## Management Commands

| Command | Description |
|---------|-------------|
| `python manage.py generate_fake_data` | Creates 5 sample chicks + random readings + 2 unknown chick alerts |
| `python manage.py simulate_readings --count 10` | Generates N random thermal readings (auto-creates chicks + fever alerts) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/monitor/` | Submit temperature reading (`{"temp": 40.2}`) |
| GET | `/api/monitor/` | Placeholder response |
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/redoc/` | ReDoc |
| GET | `/api/schema/` | OpenAPI schema |

---

## Dashboard Routes

| URL | View | Description |
|-----|------|-------------|
| `/login` | Login | Authentication |
| `/` | Dashboard Home | Overview + live alerts |
| `/alerts/` | Alert List | Full paginated alert history |
| `/dashboard/partial/` | HTMX Partial | Auto-refreshing alerts block |
| `/alerts/partial/` | HTMX Partial | Alerts table partial |
| `/alerts/resolve/<id>/` | Resolve Alert | Mark alert as resolved |
| `/admin/` | Django Admin | Admin panel |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12+, Django 5.2.4 |
| REST API | Django REST Framework 3.16.1 |
| API Docs | drf-spectacular (Swagger + ReDoc) |
| Frontend | HTMX 1.26.0, Bootstrap 5, Tailwind CSS v4 |
| Database | SQLite (default) |
| Pi Hardware | Adafruit AMG8833, OpenCV, RPi.GPIO, PySerial |

---

## Project Structure

```
chick-thermo-system/
├── manage.py                     # Django entry point
├── requirements.txt              # Server dependencies
├── config/                       # Django project config
│   ├── settings.py
│   ├── urls.py                   # Root URL routing
│   ├── wsgi.py / asgi.py
├── monitor/                      # Main Django app
│   ├── models.py                 # Chick, TemperatureReading, FeverAlert
│   ├── views.py                  # Dashboard + alert views
│   ├── urls.py                   # App URL routing
│   ├── admin.py                  # Admin registrations
│   ├── api/
│   │   ├── views.py              # DRF API endpoint
│   │   └── serializers.py        # TempSerializer
│   ├── management/commands/      # generate_fake_data, simulate_readings
│   └── templates/monitor/        # Django templates + HTMX partials
├── raspberry/                    # Raspberry Pi client
│   ├── requirements.txt          # Pi hardware dependencies
│   └── thermal_monitor_ui.py     # Tkinter GUI + sensor client
└── static/                       # CSS, JS (HTMX, Tailwind)
```
