# -*- coding: utf8 -*-

import json
import datetime
from django.http import HttpResponse
from django.shortcuts import redirect
from schedule.models import Office, Room, ScheduleSet, ScheduleRegular, Teacher, Student, Subject
from annoying.decorators import ajax_request, render_to
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

from dateutil.relativedelta import relativedelta
import chromelogger as console

def parse_date(date):
    return datetime.datetime.strptime(date, '%d-%m-%Y').date()

def get_start_date(date):
    'Returns the datetime of Monday of the current week'
    return date - datetime.timedelta(days=date.weekday())

def get_end_date(start_date):
    return start_date + relativedelta(weeks=1)

def logout_view(request):
    logout(request)
    return redirect('/login')

def ajax_apply_settings(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'settings' in POST:
            session_settings = json.loads(POST.get('settings'))
            for setting in session_settings:
                request.session[setting] = session_settings[setting]
    return HttpResponse()


@login_required
def schedule(request, date):
    def get_schedule(schedule_type):
        '''
            Returns a json of a dict of set schedule starting from Monday of the current week
        '''
        output = {}
        if schedule_type == 'set':
            schedules = ScheduleSet.objects.filter(date__gte=start_date, date__lte=end_date)
        elif schedule_type == 'regular':
            schedules = ScheduleRegular.objects.all()

        schedules = schedules.filter(**filters)
        for schedule in schedules:
            if schedule_type == 'set':
                date = schedule.date
            elif schedule_type == 'regular':
                date = start_date + datetime.timedelta(schedule.weekday)
                date = datetime.datetime.combine(date, schedule.time)
            code = '%d_%s' % (schedule.room.pk, date.strftime('%d%m%Y_%H'))
            output[code] = {
                'teacher': schedule.teacher.get_name(),
                'room': schedule.room.get_full_name(),
                'subject': schedule.subject.name,
                'lesson_type': schedule.lesson_type.name,
                'students': [student.name for student in schedule.students.all()],
            }
        return output

    def get_teachers():
        teachers = Teacher.objects.filter(**filters_subjects)
        # if student is not None:
        #     schedules = schedules_set.filter(students__pk=student)
        #     teachers_ids = [schedule.teacher.pk for schedule in schedules]
        #     teachers = teachers.filter(pk__in=teachers_ids)
        return [{'id': teacher.pk, 'name': teacher.get_name()} for teacher in teachers]

    def get_students():
        students = Student.objects.filter(**filters_subjects)
        # if teacher is not None:
        #     schedules = schedules_set.filter(teacher__pk=teacher)
        #     students_ids = set(())
        #     for schedule in schedules:
        #         students = schedule.students.all()
        #         for student in students:
        #             students_ids.add(student.pk)
        #     students = students.filter(pk__in=students_ids)
        return [{'id': student.pk, 'name': student.name} for student in students]

    def get_subjects():
        subjects = Subject.objects.all()
        if teacher is not None:
            subjects = subjects.filter(pk__in=Teacher.objects.get(pk=teacher).subjects.all())
        if student is not None:
            subjects = subjects.filter(pk__in=Student.objects.get(pk=student).subjects.all())
        return [{'id': subject.pk, 'name': subject.name} for subject in subjects]

    teacher = request.GET.get('teacher', None)
    student = request.GET.get('student', None)
    subject = request.GET.get('subject', None)
    filters = {}
    filters_subjects = {}
    if teacher is not None:
        filters['teacher__pk'] = teacher
    if student is not None:
        filters['students__pk'] = student
    if subject is not None:
        filters['subject__pk'] = subject
        filters_subjects['subjects__pk'] = subject

    start_date = get_start_date(parse_date(date))
    end_date = get_end_date(start_date)

    schedule_set = get_schedule('set')
    schedule_regular = get_schedule('regular')

    teachers = get_teachers()
    students = get_students()
    subjects = get_subjects()

    result = {
        'schedule_set': schedule_set,
        'schedule_regular': schedule_regular,
        'teachers': teachers,
        'students': students,
        'subjects': subjects,
    }

    return HttpResponse(json.dumps(result), content_type="application/json")

@render_to('home.html')
@login_required
def home(request, date=None):
    def initialize_session_values():
        if 'filters' not in request.session:
            request.session['filters'] = 'filters'
        if 'mode' not in request.session:
            request.session['mode'] = 0

    def get_date_range():
        'Returns a list of successive datetimes starting from Monday of the current week till Sunday'
        def daterange():
            dates = []
            for n in range(int ((end_date - start_date).days)):
                dates.append(start_date + datetime.timedelta(n))
            return dates
        end_date = get_end_date(start_date)
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

    def get_start_dates():
        return [
            start_date - datetime.timedelta(days=7),
            start_date,
            start_date + datetime.timedelta(days=7)
        ]

    initialize_session_values()
    hours = get_hours_ranges()
    if date is not None:
        date = parse_date(date)
    else:
        date = datetime.date.today()
    start_date = get_start_date(date)


    return {
        'hours': hours,
        'dates': get_date_range(),
        'offices': get_offices(),
        'rooms': get_rooms(),
        'start_dates': get_start_dates(),
    }