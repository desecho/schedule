# -*- coding: utf8 -*-

import re
import json
import datetime
from django.http import HttpResponse
from django.shortcuts import redirect
from schedule.models import Office, Room, ScheduleSet, ScheduleRegular, Teacher, Student, Subject, LessonType
from annoying.decorators import ajax_request, render_to
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

from dateutil.relativedelta import relativedelta
import chromelogger as console

DATE_HOUR_CODE_FORMAT = '%d%m%Y_%H'

def create_id_value_list(input):
    return [{'id': x.pk, 'name': x.name} for x in input]

def create_teachers_id_value_list(input):
    return [{'id': x.pk, 'name': x.get_name()} for x in input]

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

def get_room_and_date(room_hour_code):
    match = re.match('(\d+)_(.+)', room_hour_code)
    room_id = match.group(1)
    date = datetime.datetime.strptime(match.group(2), DATE_HOUR_CODE_FORMAT)
    return (room_id, date)

def get_schedule(schedule_mode, id):
    if schedule_mode == '0':
        schedule = ScheduleSet
    elif schedule_mode == '1':
        schedule = ScheduleRegular
    return schedule.objects.get(pk=id)

@ajax_request
@login_required
def ajax_save_schedule(request):
    def is_no_conflicts(data):
        del data['subject']
        del data['lesson_type']
        del data['teacher']
        n = schedule.objects.filter(**data).count()
        return n == 0

    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        subject = POST.get('subject')
        lesson_type = POST.get('lesson_type')
        teacher = POST.get('teacher')
        students = json.loads(POST.get('students'))
        schedule_mode = POST.get('schedule_mode')

        subject = Subject.objects.get(pk=subject)
        lesson_type = LessonType.objects.get(pk=lesson_type)
        teacher = Teacher.objects.get(pk=teacher)
        students = Student.objects.filter(pk__in=students)

        if 'schedule_id' in POST:
            schedule_id = POST['schedule_id']
            schedule = get_schedule(schedule_mode, schedule_id)

            schedule.subject = subject
            schedule.lesson_type = lesson_type
            schedule.teacher = teacher
            schedule.save()
        else:
            room_hour_code = POST.get('room_hour_code')
            room_id, date = get_room_and_date(room_hour_code)

            data = {
                'subject': subject,
                'lesson_type': lesson_type,
                'teacher': teacher,
                'room': Room.objects.get(pk=room_id),
            }
            if schedule_mode == '0':
                data['date'] = date
                schedule = ScheduleSet
            elif schedule_mode == '1':
                data['weekday'] = date.weekday()
                data['time'] = date.time()
                schedule = ScheduleRegular
            if is_no_conflicts(dict(data)):
                schedule = schedule(**data)
                schedule.save()
            else:
                return {'success': False, 'error': 'Конфликт расписания'}
        schedule.students = students
    return {'success': True}

@login_required
def ajax_delete_schedule(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        schedule_id = POST.get('schedule_id', None)
        schedule_mode = POST.get('schedule_mode', None)
        get_schedule(schedule_mode, schedule_id).delete()
    return HttpResponse()

@ajax_request
@login_required
def ajax_teachers_and_students(request):
    subject_id = request.GET.get('subject_id', None)
    teachers = create_teachers_id_value_list(Teacher.objects.filter(subjects__pk=subject_id))
    students = create_id_value_list(Student.objects.filter(subjects__pk=subject_id))
    result = {
        'teachers': teachers,
        'students': students,
    }
    return result

@ajax_request
@login_required
def ajax_room_hour(request):
    def get_schedule(schedule_mode, room_hour_code):
        room_id, date = get_room_and_date(room_hour_code)
        if schedule_mode == '0':
            schedule = ScheduleSet.objects.get(date=date, room__pk=room_id)
        elif schedule_mode == '1':
            schedule = ScheduleRegular.objects.get(weekday=date.weekday(), room__pk=room_id, time=date.time())
        return schedule
    schedule_mode = request.GET.get('schedule_mode', None)
    room_hour_code = request.GET.get('room_hour_code', None)
    schedule = get_schedule(schedule_mode, room_hour_code)
    result = {
        'teacher': {'id': schedule.teacher.pk, 'name': schedule.teacher.get_name()},
        'room': {'id': schedule.room.pk, 'name': schedule.room.get_full_name()},
        'subject': {'id': schedule.subject.pk, 'name': schedule.subject.name},
        'lesson_type': {'id': schedule.lesson_type.pk, 'name': schedule.lesson_type.name},
        'students': create_id_value_list(schedule.students.all()),
        'schedule_id': schedule.pk
    }

    return result


@ajax_request
@login_required
def ajax_schedule(request, date):
    def get_schedule(schedule_type):
        '''
            Returns a json of a dict of set schedule starting from Monday of the current week
        '''
        output = []
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
            code = '%d_%s' % (schedule.room.pk, date.strftime(DATE_HOUR_CODE_FORMAT))
            output.append(code)
        return output

    def get_teachers_filter():
        teachers = Teacher.objects.filter(**filters_subjects)
        return create_teachers_id_value_list(teachers)

    def get_students_filter():
        students = Student.objects.filter(**filters_subjects)
        return create_id_value_list(students)

    def get_lesson_types_filter():
        lesson_types = LessonType.objects.all()
        return create_id_value_list(lesson_types)

    def get_subjects_filter():
        subjects = Subject.objects.all()
        if teacher != '':
            subjects = subjects.filter(pk__in=Teacher.objects.get(pk=teacher).subjects.all())
        if student != '':
            subjects = subjects.filter(pk__in=Student.objects.get(pk=student).subjects.all())
        return create_id_value_list(subjects)

    teacher = request.GET.get('teacher', '')
    student = request.GET.get('student', '')
    subject = request.GET.get('subject', '')
    lesson_type = request.GET.get('lesson_type', '')
    filters = {}
    filters_subjects = {}
    if teacher != '':
        filters['teacher__pk'] = teacher
    if lesson_type != '':
        filters['lesson_type__pk'] = lesson_type
    if student != '':
        filters['students__pk'] = student
    if subject != '':
        filters['subject__pk'] = subject
        filters_subjects['subjects__pk'] = subject

    start_date = get_start_date(parse_date(date))
    end_date = get_end_date(start_date)

    schedule_set = get_schedule('set')
    schedule_regular = get_schedule('regular')

    teachers_filter = get_teachers_filter()
    students_filter = get_students_filter()
    subjects_filter = get_subjects_filter()
    lesson_types_filter = get_lesson_types_filter()

    result = {
        'schedule_set': schedule_set,
        'schedule_regular': schedule_regular,
        'teachers': teachers_filter,
        'students': students_filter,
        'subjects': subjects_filter,
        'lesson_types': lesson_types_filter,
    }

    return result

@render_to('admin-schedule.html')
@login_required
def admin_schedule(request, date=None):
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

    def get_lesson_types():
        output = create_id_value_list(LessonType.objects.all())
        return json.dumps(output)

    def get_subjects():
        output = create_id_value_list(Subject.objects.all())
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
        hours = [str(x).zfill(2) for x in hours]
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
        'lesson_types': get_lesson_types(),
        'subjects': get_subjects(),
        'start_dates': get_start_dates(),
    }

@render_to('teacher-schedule.html')
@login_required
def teacher_schedule(request, date=None):
    def initialize_session_values():
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

    def get_lesson_types():
        output = create_id_value_list(LessonType.objects.all())
        return json.dumps(output)

    def get_subjects():
        output = create_id_value_list(Subject.objects.all())
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
        hours = [str(x).zfill(2) for x in hours]
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
        'lesson_types': get_lesson_types(),
        'subjects': get_subjects(),
        'start_dates': get_start_dates(),
    }