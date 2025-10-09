from django.shortcuts import render, get_object_or_404, redirect
from .models import Chick, FeverAlert
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import time


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard_home")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "monitor/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard_home(request):
    chicks = Chick.objects.all()
    active_alerts = FeverAlert.objects.filter(resolved=False).order_by('-recorded_at')

    paginator = Paginator(active_alerts, 5)  # show 5 alerts per page
    page_number = request.GET.get("page")
    active_alerts = paginator.get_page(page_number)

    return render(request, 'monitor/dashboard_home.html', {
        'chicks': chicks,
        'active_alerts': active_alerts
    })

@login_required
def dashboard_partial(request):
    """Return only the alerts partial (for HTMX refresh & pagination)"""
    alerts = FeverAlert.objects.filter(resolved=False).order_by('-recorded_at')

    paginator = Paginator(alerts, 5)
    page_number = request.GET.get("page") or 1   # default to page 1
    active_alerts = paginator.get_page(page_number)
    return render(request, 'monitor/partials/dashboard_partial.html', {
        'active_alerts': active_alerts,
    })

@login_required
def alert_list(request):
    alerts = FeverAlert.objects.all().order_by('-recorded_at')
    return render(request, 'monitor/alerts.html', {'alerts': alerts})

@login_required
def resolve_alert(request, alert_id):
    alert = get_object_or_404(FeverAlert, id=alert_id)
    alert.resolved = True
    alert.resolved_at = now()
    alert.save()
    return redirect('alert_list')
