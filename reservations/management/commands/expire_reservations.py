from django.core.management.base import BaseCommand
from reservations.services import expire_reservations

class Command(BaseCommand):
    help = 'Expires ALLOCATED reservations that have passed their expiry date.'

    def handle(self, *args, **options):
        count = expire_reservations()
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully expired {count} reservations.'))
        else:
            self.stdout.write(self.style.SUCCESS('No reservations to expire.'))
