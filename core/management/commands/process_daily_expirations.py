from django.core.management.base import BaseCommand
from django.utils import timezone
from reservations.services import expire_reservations
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Executes daily automated tasks: expires uncollected holds and updates expired membership accounts.'

    def handle(self, *args, **options):
        self.stdout.write("Running daily automated expiration check...")

        # 1. Expire uncollected hold allocations
        expired_holds_count = expire_reservations()
        self.stdout.write(self.style.SUCCESS(f"Expired {expired_holds_count} uncollected hold allocation(s)."))

        # 2. Update expired memberships
        today = timezone.now().date()
        expired_members = UserProfile.objects.filter(
            membership_status='ACTIVE',
            membership_expiry_date__lt=today
        )
        expired_members_count = expired_members.count()
        expired_members.update(membership_status='EXPIRED')

        self.stdout.write(self.style.SUCCESS(f"Updated {expired_members_count} member account(s) to EXPIRED."))
        self.stdout.write(self.style.SUCCESS("Daily expiration check completed successfully."))
