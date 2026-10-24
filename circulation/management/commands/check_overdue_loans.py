from django.core.management.base import BaseCommand
from circulation.services import scan_and_notify_overdue_loans


class Command(BaseCommand):
    help = 'Scans active loans, dispatches overdue alerts and due date reminders to patrons.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Scanning active loans for due dates and overdue statuses..."))
        result = scan_and_notify_overdue_loans()
        
        self.stdout.write(self.style.SUCCESS(
            f"Scan complete!\n"
            f" - Overdue loans flagged: {result['overdue_count']}\n"
            f" - Due soon reminders sent: {result['reminder_count']}\n"
            f" - Total accrued fines estimated: ₹{result['total_estimated_fines']:.2f}"
        ))
