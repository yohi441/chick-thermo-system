
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from monitor.models import Chick, TemperatureReading, FeverAlert
import random

class Command(BaseCommand):
    help = 'Generate fake temperature readings and alerts'

    def handle(self, *args, **kwargs):
        # Create 5 sample chicks if none exist
        if Chick.objects.count() == 0:
            for i in range(5):
                Chick.objects.create(name=f"Chick #{i+1}", tag_id=f"TAG{i+1}")
            self.stdout.write(self.style.SUCCESS("✅ Created 5 sample chicks."))

        chicks = Chick.objects.all()

        # Simulate 3 readings per chick
        for chick in chicks:
            for _ in range(3):
                temp = round(random.uniform(37.5, 40.5), 1)
                reading = TemperatureReading.objects.create(
                    chick=chick,
                    temperature=temp,
                    recorded_at=now() - timedelta(minutes=random.randint(1, 60))
                )
                self.stdout.write(f"🐥 {chick.name} - {temp}°C")

        # Create 2 high-temp alerts for unknown chicks
        for i in range(2):
            temp = round(random.uniform(39.6, 41.0), 1)
            FeverAlert.objects.create(
                chick=None,
                temperature=temp,
                recorded_at=now() - timedelta(minutes=random.randint(1, 60))
            )
            self.stdout.write(f"🔥 Unknown Chick - {temp}°C alert created")

        self.stdout.write(self.style.SUCCESS("✅ Fake data generation complete!"))
