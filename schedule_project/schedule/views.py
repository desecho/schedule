# -*- coding: utf8 -*-

import json
from django.http import HttpResponse
from django.shortcuts import redirect
from schedule.models import Office, Room, ScheduleSet, ScheduleRegular
from annoying.decorators import ajax_request, render_to
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import chromelogger as console


def logout_view(request):
    logout(request)
    return redirect('/login/')


@render_to('home.html')
@login_required
def home(request):

    def get_start_date():
        'Returns the datetime of Monday of the current week'
        today = date.today()
        return today - timedelta(days=today.weekday())

    def get_date_range():
        'Returns a list of successive datetimes starting from Monday of the current week till Sunday'
        def daterange():
            dates = []
            for n in range(int ((end_date - start_date).days)):
                dates.append(start_date + timedelta(n))
            return dates
        end_date = start_date + relativedelta(weeks=1)
        return daterange()

    def get_offices():
        '''
            Returns a list of dict containing office name and rooms
        '''
        output = []
        offices = Office.objects.all()
        for office in offices:
            rooms = Room.objects.filter(office=office)
            output.append({'name': office.name, 'rooms': rooms})
        return output

    def get_rooms():
        '''
            Returns a json with a dict {room_id: room_name}
        '''
        output = {}
        rooms = Room.objects.all()
        for room in rooms:
            output[room.pk] = room.get_full_name()
        return json.dumps(output)

    def get_hours_ranges():
        '''
        Returns rows with working hours in a row
        List of 3 lists of 4 ints.
        Example:
        [[8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19]]

        '''
        def chunks(l, n):
            'Yield successive n-sized chunks from l.'
            for i in xrange(0, len(l), n):
                yield l[i:i+n]
        hours = range(settings.WORK_TIME[0], settings.WORK_TIME[1] + 1)
        return list(chunks(hours, 4))

    def get_schedule(schedule_type):
        '''
            Returns a json of a dict of set schedule starting from Monday of the current week
        '''
        output = {}
        if schedule_type == 'set':
            schedules = ScheduleSet.objects.filter(date__gte=start_date)
        elif schedule_type == 'regular':
            schedules = ScheduleRegular.objects.all()

        for schedule in schedules:
            if schedule_type == 'set':
                date = schedule.date
            elif schedule_type == 'regular':
                date = start_date + timedelta(schedule.weekday)
                date = datetime.combine(date, schedule.time)
            code = '%d_%s' % (schedule.room.pk, date.strftime('%d%m%Y_%H'))
            output[code] = {
                'teacher': schedule.teacher.get_name(),
                'room': schedule.room.get_full_name(),
                'group_type': schedule.group_type.name,
                'students': [student.name for student in schedule.students.all()],
            }
        return json.dumps(output)

    hours = get_hours_ranges()
    start_date = get_start_date()
    schedule_set = get_schedule('set')
    schedule_regular = get_schedule('regular')

    return {
        'hours': hours,
        'dates': get_date_range(),
        'offices': get_offices(),
        'rooms': get_rooms(),
        'schedule_set': schedule_set,
        'schedule_regular': schedule_regular,
    }