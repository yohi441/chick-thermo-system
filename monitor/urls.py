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
    path("alerts/partial/", views.alert_list_partial, name="alert_list_partial"),
    path("alerts/pagination/", views.alert_pagination, name="alert_pagination"),
    path("api/monitor/", api_views.monitor, name="api"),  # New API endpoint
]

