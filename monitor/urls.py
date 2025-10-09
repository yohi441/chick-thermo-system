# monitor/urls.py

from django.urls import path
from . import views
from .api import views as api_views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('', views.dashboard_home, name='dashboard_home'),
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/resolve/<int:alert_id>/', views.resolve_alert, name='resolve_alert'),
    path("dashboard/partial/", views.dashboard_partial, name="dashboard_partial"),
    path("api/monitor/", api_views.monitor, name="api"),  # New API endpoint
]

