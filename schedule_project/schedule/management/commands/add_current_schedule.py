import datetime
from django.core.management.base import BaseCommand
from schedule.models import ScheduleRegular, ScheduleSet
from schedule.views import get_start_date_for_schedule, get_date_from_schedule, has_conflicts_on_adding

class Command(BaseCommand):
    help = 'Adds current schedule from regular schedule'

    def handle(self, *args, **options):
        schedules = ScheduleRegular.objects.all()
        start_date = get_start_date_for_schedule()
        start_date += datetime.timedelta(days=7)
        for schedule in schedules:
            data = {
                'teacher': schedule.teacher,
                'room': schedule.room,
                'lesson_type': schedule.lesson_type,
                'subject': schedule.subject,
                'date': get_date_from_schedule('regular', schedule, start_date)
            }
            schedule_set = ScheduleSet(**data)
            if has_conflicts_on_adding('self', ScheduleSet, dict(data)):
                raise Exception('Conflict')
            schedule_set.save()
            schedule_set.students = schedule.students.all()
