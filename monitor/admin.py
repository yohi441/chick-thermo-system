from django.contrib import admin
from .models import Chick, TemperatureReading, FeverAlert
from django.utils import timezone


@admin.register(Chick)
class ChickAdmin(admin.ModelAdmin):
    pass
@admin.register(TemperatureReading)
class TemperatureReadingAdmin(admin.ModelAdmin):
    pass

@admin.register(FeverAlert)
class FeverAlertAdmin(admin.ModelAdmin):
    pass
