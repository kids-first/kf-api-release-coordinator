from django.core.management.base import BaseCommand
from coordinator.api.factories.release import ReleaseFactory


class Command(BaseCommand):
    help = "Pre-populate the database with fake data"

    def handle(self, *args, **options):
        ReleaseFactory.create_batch(100)
        self.stdout.write(self.style.SUCCESS("Created releases"))
