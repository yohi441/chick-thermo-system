

from django.db import models
from django.utils import timezone


class Chick(models.Model):
    name = models.CharField(max_length=100)
    tag_id = models.CharField(max_length=50, unique=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class TemperatureReading(models.Model):
    chick = models.ForeignKey(Chick, on_delete=models.CASCADE, related_name='readings')
    temperature = models.FloatField()
    recorded_at = models.DateTimeField(default=timezone.now)

    @property
    def is_fever(self):
        return self.temperature >= 39.5  # Example fever threshold

    def __str__(self):
        return f"{self.chick.name} - {self.temperature}°C at {self.recorded_at}"


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.temperature >= 39.5:
            FeverAlert.objects.get_or_create(
                chick=self.chick,
                temperature=self.temperature,
                recorded_at=self.recorded_at,
                resolved=False
            )


class FeverAlert(models.Model):
    chick = models.ForeignKey(Chick, on_delete=models.CASCADE, null=True, blank=True)
    temperature = models.FloatField()
    recorded_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"⚠️ Fever Alert for {self.chick} at {self.temperature}°C"


