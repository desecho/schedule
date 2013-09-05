from django.core.management.base import BaseCommand
from schedule.models import ScheduleRegular, ScheduleSet

class Command(BaseCommand):
    help = 'Adds current schedule from persistent schedule'

    def handle(self, *args, **options):
        schedules = ScheduleRegular.objects.all()

