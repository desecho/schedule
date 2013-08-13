# -*- coding: utf8 -*-

import json
from django.http import HttpResponse
from django.shortcuts import redirect
from schedule.models import Office
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
    def getDateRange():
        def daterange(start_date, end_date):
            for n in range(int ((end_date - start_date).days)):
                yield start_date + timedelta(n)
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + relativedelta(weeks=1)
        return daterange(start_date, end_date)

    hours = range(settings.WORK_TIME[0], settings.WORK_TIME[1] + 1)
    dates = getDateRange()
    offices = Office.objects.all()

    return {'hours': hours, 'dates': dates, 'rooms': rooms}
