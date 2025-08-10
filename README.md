# 🐥 Chick Fever Detection Dashboard (Prototype)

This is a Django-based prototype for detecting fever in chicks using thermal imaging (simulated for now).  
When a chick's temperature exceeds a set threshold, the system raises a fever alert and displays it in a real-time dashboard (auto-refresh with HTMX).

---

## 📦 Requirements
- Python 3.12+
- pip
- Virtualenv (recommended)
- Django 5.2.4

---
Create & activate a virtual environment

python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate 

Install dependencies

pip install -r requirements.txt
Apply database migrations

python manage.py migrate
Create a superuser

python manage.py createsuperuser
Run the development server

python manage.py runserver
