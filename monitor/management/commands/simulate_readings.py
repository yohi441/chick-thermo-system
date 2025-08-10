# monitor/management/commands/simulate_readings.py
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from monitor.models import Chick, TemperatureReading

class Command(BaseCommand):
    help = "Simulates thermal readings for chicks."

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of simulated readings to generate.'
        )

    def handle(self, *args, **options):
        count = options['count']

        for _ in range(count):
            # 50% chance to pick an existing chick
            if Chick.objects.exists() and random.choice([True, False]):
                chick = random.choice(list(Chick.objects.all()))
            else:
                # Create a new "unknown" chick with unique tag
                tag_id = f"U{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
                chick = Chick.objects.create(
                    name=f"Unknown Chick {timezone.now().strftime('%H%M%S')}",
                    tag_id=tag_id
                )
                self.stdout.write(self.style.WARNING(f"Created new unknown chick: {chick.name} ({tag_id})"))

            # Generate random temperature
            temp = round(random.uniform(37.0, 42.5), 2)

            # Create reading (this will auto-trigger FeverAlert if >= 39.5°C)
            TemperatureReading.objects.create(
                chick=chick,
                temperature=temp
            )

            if temp >= 39.5:
                self.stdout.write(self.style.ERROR(f"⚠️ ALERT: {chick.name} at {temp}°C"))
            else:
                self.stdout.write(self.style.SUCCESS(f"{chick.name} at {temp}°C"))

        self.stdout.write(self.style.SUCCESS("✅ Simulation completed."))
