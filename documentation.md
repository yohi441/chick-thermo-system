# Chick Fever Detection System — Technical Documentation

## 1. System Architecture

The system is divided into two tiers:

### Tier 1: Raspberry Pi Sensor Node
Runs `raspberry/thermal_monitor_ui.py` — a standalone Python application with a Tkinter GUI. It reads temperature data from an **Adafruit AMG8833** 8x8 IR thermal array sensor over I2C, visualizes it via OpenCV, and pushes readings to the Django server via REST API. It also controls a buzzer (GPIO) and a SIM900 GSM module (serial) for local and remote alerts.

### Tier 2: Django Web Dashboard
A Django 5.2 application that provides:
- **REST API endpoint** — accepts temperature data from the Pi
- **Database models** — stores chicks, readings, and fever alerts
- **HTMX-powered dashboard** — real-time alert updates without page reloads
- **Admin interface** — Django admin for data management
- **API documentation** — auto-generated Swagger UI / ReDoc

```
┌──────────────────────────────────────────────────────────────────┐
│ Raspberry Pi (thermal_monitor_ui.py)                             │
│                                                                  │
│  ┌──────────────┐   ┌───────────────┐   ┌────────────────────┐  │
│  │ AMG8833 I2C  │──>│ OpenCV Viz    │──>│ POST /api/monitor/ │──┼────┐
│  │ (or sim)     │   │ (color map)   │   │ {temp: float}      │  │    │
│  └──────────────┘   └───────────────┘   └────────────────────┘  │    │
│                                                      │           │    │
│  ┌──────────────┐   ┌───────────────┐               │           │    │
│  │ Buzzer GPIO  │<──│ Threshold     │<── config.json│           │    │
│  │ (pin 17)     │   │ Check         │               │           │    │
│  └──────────────┘   └───────────────┘               │           │    │
│                                                      │           │    │
│  ┌──────────────────────┐                            │           │    │
│  │ SIM900 GSM (Serial)  │<───────────────────────────┘           │    │
│  │ (SMS Alerts)         │                                        │    │
│  └──────────────────────┘                                        │    │
└──────────────────────────────────────────────────────────────────┘    │
                                                                        │
┌───────────────────────────────────────────────────────────────────────┘
│
┌──────────────────────────────────────────────────────────────────────┐
│ Django Server (Dashboard)                                            │
│                                                                      │
│  POST /api/monitor/                                                  │
│       │                                                              │
│       ▼                                                              │
│  ┌──────────┐    ┌──────────────────────┐    ┌───────────────────┐   │
│  │DRF View  │───>│ TemperatureReading   │───>│ FeverAlert        │   │
│  │(api_view)│    │ (auto-alert on save  │    │ (resolved/active) │   │
│  └──────────┘    │  if >= 39.5 C)       │    └───────────────────┘   │
│                  └──────────────────────┘              │              │
│                                                        │              │
│  ┌─────────────────────────────────────────────────────┘              │
│  │                                                                     │
│  ▼                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │ HTMX Dashboard                                                 │    │
│  │  ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐   │    │
│  │  │ dashboard/   │──>│ alerts/          │──>│ resolve/<id>/│   │    │
│  │  │ partial/     │   │ partial/         │   │ (HTMX)       │   │    │
│  │  │ (refreshes   │   │ (table + pages)  │   └──────────────┘   │    │
│  │  │  every 2s)   │   └──────────────────┘                      │    │
│  │  └──────────────┘                                             │    │
│  └───────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Models

All models are defined in `monitor/models.py`.

### Chick

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Display name (e.g., "Chick #1" or "Unknown Chick 143022") |
| `tag_id` | CharField(50, unique) | Unique identifier tag (e.g., "TAG1" or auto-generated "U20250101143022000000") |
| `date_added` | DateTimeField(auto) | Timestamp of when the chick was registered |

**Methods:** `__str__` returns the chick's name.

### TemperatureReading

| Field | Type | Description |
|-------|------|-------------|
| `chick` | ForeignKey(Chick) | The chick this reading belongs to |
| `temperature` | FloatField | Recorded temperature in Celsius |
| `recorded_at` | DateTimeField(auto) | When the reading was taken |

**Properties:** `is_fever` — returns `True` if temperature >= 39.5 C.

**`save()` override:** Automatically creates a `FeverAlert` via `get_or_create` when temperature >= 39.5 C. The alert is created with `resolved=False`.

### FeverAlert

| Field | Type | Description |
|-------|------|-------------|
| `chick` | ForeignKey(Chick, null) | The chick with fever (nullable for unknown chicks) |
| `temperature` | FloatField | The fever temperature reading |
| `recorded_at` | DateTimeField(auto) | When the fever was detected |
| `resolved` | BooleanField(default=False) | Whether the alert has been handled |
| `resolved_at` | DateTimeField(null) | When the alert was resolved |

---

## 3. REST API Reference

All API endpoints are documented in Swagger at `/api/docs/` and ReDoc at `/api/redoc/`.

### POST /api/monitor/

Accepts a temperature reading and creates a new chick + fever alert.

**Request:**
```json
{
  "temp": 40.2
}
```

**Response (201 Created):**
```json
{
  "message": 40.2
}
```

**Behavior:**
- Creates a new `Chick` with auto-generated `name` ("Unknown Chick HHMMSS") and `tag_id` ("UYYYYMMDDHHMMSSffffff").
- Creates a `FeverAlert` directly (skips `TemperatureReading` creation — the commented-out code in the API view suggests this is intentional for the prototype).
- Does **not** create a `TemperatureReading` in the current implementation.

### GET /api/monitor/

**Response (200):**
```json
{
  "message": "this is example of the api get request"
}
```

### GET /api/schema/

Returns the raw OpenAPI 3.0 schema (YAML/JSON depending on `Accept` header).

---

## 4. Dashboard Views & URL Map

| URL Pattern | View Function | Template | Auth Required | Description |
|-------------|---------------|----------|---------------|-------------|
| `/login/` | `login_view` | `monitor/login.html` | No | POST login form |
| `/logout/` | `logout_view` | — | No | Clears session, redirects to login |
| `/` | `dashboard_home` | `monitor/dashboard_home.html` | Yes | Overview card + active alerts with auto-refresh |
| `/alerts/` | `alert_list` | `monitor/alerts.html` | Yes | Full paginated alert table |
| `/dashboard/partial/` | `dashboard_partial` | `monitor/partials/dashboard_partial.html` | Yes | HTMX partial — refreshes every 2s |
| `/alerts/partial/` | `alert_list_partial` | `monitor/partials/alerts_partial.html` | Yes | HTMX partial for table body |
| `/alerts/pagination/` | `alert_pagination` | `monitor/partials/alerts_partial.html` | Yes | Paginated table partial |
| `/alerts/resolve/<int:alert_id>/` | `resolve_alert` | `monitor/partials/alerts_partial.html` | Yes | Sets `resolved=True`, returns partial |
| `/admin/` | Django Admin | — | Yes (staff) | Built-in admin interface |

### View Details

**`dashboard_home`** — The main landing page. Loads all chicks and unresolved alerts (paginated 5 per page). Passes `unresolved_alerts_count` for badge rendering.

**`dashboard_partial`** — HTMX endpoint that returns only the alerts list partial. Used by the `hx-trigger="every 2s"` on the dashboard for live updates.

**`alert_list`** — Shows all alerts (active and resolved), paginated 10 per page.

**`resolve_alert`** — HTMX-only endpoint (checks `request.htmx`). Sets `resolved=True` and `resolved_at=now()`, then returns the alerts partial.

**`alert_pagination`** — Returns the alerts partial with pagination for the alerts table page.

### Pagination

- Dashboard alerts: **5 per page**
- Alerts table: **10 per page**
- Pagination is handled via `django.core.paginator.Paginator` in views
- Page navigation uses HTMX `hx-get` requests with `hx-target="#alerts-container"` and `hx-swap="outerHTML"`

---

## 5. HTMX Behavior

### Auto-Refresh on Dashboard

The dashboard alerts container has:
```html
<div id="alerts-container"
     hx-get="{% url 'dashboard_partial' %}?page={{ active_alerts.number }}"
     hx-trigger="every 2s"
     hx-swap="outerHTML"
     hx-push-url="false">
```

This polls the server every 2 seconds and replaces the entire alerts container. The page number is preserved during refresh.

### Out-of-Band (OOB) Swaps

The `dashboard_partial.html` template uses `hx-swap-oob="true"` on two elements to update the dashboard badge and navigation badge simultaneously:

```html
<span id="alert-count-dashboard" hx-swap-oob="true">...</span>
<span id="nav-alert-count" hx-swap-oob="true">...</span>
```

This means any HTMX response from any endpoint that includes these OOB elements will update the alert badge counts across the entire page.

### Resolve Action

Clicking "Resolve" sends an HTMX GET request to `/alerts/resolve/<id>/`. The server:
1. Marks the alert as resolved
2. Returns the alerts partial (which replaces `#alerts-container`)
3. The OOB span updates the badge counts

### CSRF Handling

The `<body>` tag includes `hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'` to automatically include the CSRF token on all HTMX requests.

---

## 6. Raspberry Pi Client Guide

### File: `raspberry/thermal_monitor_ui.py`

This is a standalone application that runs on a Raspberry Pi. It creates a Tkinter GUI with configuration fields and monitoring controls.

#### Configuration (`config.json`)

Auto-created on first run with defaults. Stored alongside the script.

| Key | Default | Description |
|-----|---------|-------------|
| `threshold` | `30.0` | Temperature threshold in Celsius that triggers alerts |
| `phone_number` | `"+639XXXXXXXXX"` | Destination number for SMS alerts |
| `message` | `"Alert! Temperature threshold exceeded."` | SMS message body |
| `sms_enabled` | `true` | Whether to send SMS alerts |
| `buzzer_enabled` | `true` | Whether to sound buzzer on alert |
| `sensor_interval` | `2` | Seconds between sensor readings |
| `api_url` | `""` | Django API URL (e.g., `http://192.168.1.100:8000/api/monitor/`) |

#### Hardware Wiring

| Component | Connection |
|-----------|------------|
| **AMG8833** | I2C (SDA = GPIO 2, SCL = GPIO 3, VCC = 3.3V, GND = GND) |
| **Buzzer** | GPIO 17 (BCM) + GND |
| **SIM900** | UART Serial (`/dev/serial0`, 9600 baud) |

#### Sensor Readout

The AMG8833 returns an 8x8 grid of temperature values. The script:
1. Reads the 8x8 array via `adafruit_amg88xx`
2. Computes the max temperature across all 64 pixels
3. Displays an OpenCV window with the thermal map (color-mapped via `COLORMAP_INFERNO`, scaled 240x240)
4. Overlays the max temperature text on the frame

If no sensor is detected, `numpy.random.uniform(25.0, 35.0, (8, 8))` is used instead.

#### Alert Flow

1. `max_temp > threshold` triggers:
   - **Buzzer** — GPIO 17 HIGH for 1 second
   - **SMS** — sends via SIM900 AT commands to configured phone number
   - **API POST** — sends `{"temp": max_temp}` to `config["api_url"]`
2. A cooldown of 2 seconds follows each alert trigger

#### Main Loop

Runs in a daemon thread. The OpenCV window listens for the 'q' key to stop monitoring. The Tkinter GUI provides Start/Stop buttons.

---

## 7. Management Commands Reference

### `generate_fake_data`

Creates sample data for testing the dashboard.

```bash
python manage.py generate_fake_data
```

**What it does:**
- If no chicks exist, creates 5 (`Chick #1` through `Chick #5`)
- For each chick, creates 3 temperature readings (37.5 C – 40.5 C, random)
- Creates 2 fever alerts for unknown (null chick) chicks at 39.6 C – 41.0 C

### `simulate_readings`

Generates custom numbers of simulated thermal readings.

```bash
python manage.py simulate_readings --count 10
```

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--count` | `5` | Number of simulated readings to generate |

**Behavior:**
- 50% chance of picking an existing random chick
- 50% chance of creating a new "Unknown Chick" with auto-generated tag
- Temperature range: 37.0 C – 42.5 C
- If temperature >= 39.5 C, a `FeverAlert` is auto-created via the `TemperatureReading.save()` method

---

## 8. Static Files & Styling

### Tailwind CSS v4

- Source: `static/css/input.css` (single `@import "tailwindcss"` directive)
- Compiled output: `static/css/output.css` (~645 lines)
- To rebuild: `npx tailwindcss -i static/css/input.css -o static/css/output.css`

### Bootstrap 5

Loaded via CDN in `base.html`:
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
```
Used primarily for the login form styling (`.container`, `.card`, `.form-control`, etc.).

### HTMX

- Library: `static/js/htmx.min.js` (v1.26.0)
- Django integration: `django-htmx` package provides `{% htmx_script %}` and `{% django_htmx_script %}` template tags
- HTMX indicators styled in `base.html` with `.htmx-indicator` CSS (hidden by default, shown during request)

---

## 9. Settings Overview

Key settings from `config/settings.py`:

| Setting | Value | Notes |
|---------|-------|-------|
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `['*']` | Restrict in production |
| `TIME_ZONE` | `'Asia/Manila'` | Adjust for your location |
| `DATABASES` | SQLite (`db.sqlite3`) | Swap for PostgreSQL in production |
| `STATICFILES_DIRS` | `[BASE_DIR / 'static']` | Static file directory |
| `LOGIN_REDIRECT_URL` | `'/'` | Redirect after login |
| `LOGIN_URL` | `'/login'` | Login page URL |
| `REST_FRAMEWORK` | JSON renderer only, drf-spectacular schema | |
| `SPECTACULAR_SETTINGS` | Title "My API", version 1.0.0 | Customize for production |

### Installed Apps

- **Django built-in:** admin, auth, contenttypes, sessions, messages, staticfiles
- **Project:** `monitor`
- **Third-party:** `rest_framework`, `drf_spectacular`, `django_htmx`

### Middleware

Standard Django middleware stack with `django_htmx.middleware.HtmxMiddleware` added at the end for HTMX request detection.

---

## 10. Deployment Notes

### Production Checklist

1. **Set `DEBUG = False`** in `config/settings.py`
2. **Set `ALLOWED_HOSTS`** to your domain/IP (e.g., `['chick-monitor.example.com']`)
3. **Change `SECRET_KEY`** to a unique, unpredictable value
4. **Collect static files:** `python manage.py collectstatic`
5. **Configure a production database** (PostgreSQL recommended over SQLite)
6. **Use a production WSGI server** (Gunicorn + Nginx, or Daphne for ASGI)

### Example: Gunicorn + Nginx

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Nginx reverse proxy configuration would proxy `/` to `localhost:8000` and serve static files directly.

### Static Files in Production

Run `python manage.py collectstatic` and configure a `STATIC_ROOT` setting. Point Nginx (or your reverse proxy) to serve the collected static directory.

---

## 11. Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `ImportError: No module named 'board'` | Missing hardware libraries | Run on actual Raspberry Pi or install `Adafruit-Blinka` |
| AMG8833 not detected | I2C not enabled or wiring wrong | Run `sudo raspi-config` → Interface Options → I2C → Enable; check wiring |
| SIM900 not responding | Serial port wrong or module not powered | Verify `/dev/serial0` exists; check baud rate (9600) |
| Dashboard shows no alerts | No data in database | Run `python manage.py generate_fake_data` |
| HTMX not refreshing | Server not running or URL mismatch | Check Django server is running; verify network connectivity |
| Alerts not resolving | CSRF token missing | Ensure HTMX headers include CSRF token (handled in `base.html`) |
| OpenCV window not showing | No display (SSH) or missing GUI libs | Run on Pi desktop or install `python3-tk`; use VNC/HDMI |
| Buzzer not sounding | Wrong GPIO pin or permission | Check wiring (GPIO 17); run with `sudo` if needed |
