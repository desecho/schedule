# -*- coding: utf8 -*-

import json
from django.http import HttpResponse
from django.shortcuts import redirect
from schedule.models import Office, Room, ScheduleSet
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
        today = date.today()
        return today - timedelta(days=today.weekday())

    def get_date_range():
        def daterange():
            dates = []
            for n in range(int ((end_date - start_date).days)):
                dates.append(start_date + timedelta(n))
            return dates
        end_date = start_date + relativedelta(weeks=1)
        return daterange()

    def get_offices():
        output = []
        offices = Office.objects.all()
        for office in offices:
            rooms = Room.objects.filter(office=office)
            output.append({'name': office.name, 'rooms': rooms})
        return output

    def get_hours_ranges():
        def chunks(l, n):
            'Yield successive n-sized chunks from l.'
            for i in xrange(0, len(l), n):
                yield l[i:i+n]
        hours = range(settings.WORK_TIME[0], settings.WORK_TIME[1] + 1)
        return list(chunks(hours, 4))

    def get_schedules():
        output = []
        schedules = ScheduleSet.objects.filter(date__gte=start_date)
        for schedule in schedules:
            code = '%d_%s' % (schedule.room.pk, schedule.date.strftime('%d%m%Y_%H'))
            output.append(code)
        return json.dumps(output)

    hours = get_hours_ranges()
    start_date = get_start_date()
    dates = get_date_range()
    offices = get_offices()

    schedules = get_schedules()


    return {'hours': hours, 'dates': dates, 'offices': offices, 'schedules': schedules}
