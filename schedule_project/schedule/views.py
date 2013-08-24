# -*- coding: utf8 -*-

import re
import json
import datetime
from django.http import HttpResponse
from django.shortcuts import redirect
from schedule.models import Office, Room, ScheduleSet, ScheduleRegular, Teacher, Student, Subject, LessonType, DAYS_OF_THE_WEEK
from annoying.decorators import ajax_request, render_to
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

from dateutil.relativedelta import relativedelta
import chromelogger as console

DATE_HOUR_CODE_FORMAT = '%d%m%Y_%H'

def create_id_value_list(input):
    return [{'id': x.pk, 'name': x.name} for x in input]

def create_id_value_list_full_name(input):
    return [{'id': x.pk, 'name': x.get_full_name()} for x in input]

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

def get_schedule(schedule_mode, id):
    if schedule_mode == '0':
        schedule = ScheduleSet
    elif schedule_mode == '1':
        schedule = ScheduleRegular
    return schedule.objects.get(pk=id)

def filter_schedule_by_date(schedule, schedule_mode):
    filters = {}
    if schedule_mode == '0':
        filters['date'] = schedule.date
        schedule_filter = ScheduleSet
    elif schedule_mode == '1':
        filters['weekday'] = schedule.weekday
        filters['time'] = schedule.time
        schedule_filter = ScheduleRegular
    return schedule_filter.objects.filter(**filters)

def parse_datetime(date):
    return datetime.datetime.strptime(date, DATE_HOUR_CODE_FORMAT)

def get_schedule_and_filter_params(schedule_mode, date):
    filter_params = {}
    if schedule_mode == '0':
        filter_params['date'] = date
        schedule = ScheduleSet
    elif schedule_mode == '1':
        filter_params['weekday'] = date.weekday()
        filter_params['time'] = date.time()
        schedule = ScheduleRegular
    return (schedule, filter_params)

@ajax_request
@login_required
def ajax_save_schedule(request):
    def is_no_conflicts_create(data):
        del data['subject']
        del data['lesson_type']
        del data['teacher']
        n = schedule.objects.filter(**data).count()
        return n == 0

    def is_no_conflicts_edit():
        schedule_filter = filter_schedule_by_date(schedule, schedule_mode)
        n = schedule_filter.filter(room=room).exclude(pk=schedule.pk).count()
        return n == 0

    def get_room_and_date(room_hour_code):
        match = re.match('(\d+)_(.+)', room_hour_code)
        room_id = match.group(1)
        date = parse_datetime(match.group(2))
        return (room_id, date)

    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        subject = POST.get('subject')
        lesson_type = POST.get('lesson_type')
        teacher = POST.get('teacher')
        students = json.loads(POST.get('students'))
        schedule_mode = POST.get('schedule_mode')
        room = POST.get('room', None)

        subject = Subject.objects.get(pk=subject)
        lesson_type = LessonType.objects.get(pk=lesson_type)
        teacher = Teacher.objects.get(pk=teacher)
        students = Student.objects.filter(pk__in=students)

        if room is not None:
            room = Room.objects.get(pk=room)

        if 'schedule_id' in POST:
            schedule_id = POST['schedule_id']
            schedule = get_schedule(schedule_mode, schedule_id)

            schedule.subject = subject
            schedule.lesson_type = lesson_type
            schedule.teacher = teacher
            if room is not None:
                schedule.room = room
                if is_no_conflicts_edit():
                    schedule.save()
                else:
                    return {'success': False, 'error': 'Конфликт расписания'}
            else:
                schedule.save()
        else:
            room_hour_code = POST.get('room_hour_code', None)
            hour_code = POST.get('hour_code', None)
            if room_hour_code is not None:
                room_id, date = get_room_and_date(room_hour_code)
                room = Room.objects.get(pk=room_id)
            else:
                date = parse_datetime(hour_code)
            data = {
                'subject': subject,
                'lesson_type': lesson_type,
                'teacher': teacher,
                'room': room,
            }
            schedule, filter_params = get_schedule_and_filter_params(schedule_mode, date)
            data.update(filter_params)
            if is_no_conflicts_create(dict(data)):
                schedule = schedule(**data)
                schedule.save()
            else:
                return {'success': False, 'error': 'Конфликт расписания'}

        schedule.students = students
    return {'success': True, 'id': schedule.pk}

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
    teachers = create_id_value_list_full_name(Teacher.objects.filter(subjects__pk=subject_id))
    students = create_id_value_list_full_name(Student.objects.filter(subjects__pk=subject_id))
    result = {
        'teachers': teachers,
        'students': students,
    }
    return result

def get_available_room_list(schedules):
    def get_busy_rooms(schedules):
        busy_rooms = schedules.values_list('room')
        return [x[0] for x in busy_rooms]
    busy_rooms = get_busy_rooms(schedules)
    return [x for x in create_id_value_list_full_name(Room.objects.all()) if x['id'] not in busy_rooms]

@ajax_request
@login_required
def ajax_get_room_list(request):
    schedule_mode = request.GET.get('schedule_mode', None)
    hour_code = request.GET.get('hour_code', None)
    date = parse_datetime(hour_code)
    schedule, filter_params = get_schedule_and_filter_params(schedule_mode, date)
    schedules = schedule.objects.filter(**filter_params)
    return get_available_room_list(schedules)


@ajax_request
@login_required
def ajax_get_hour_details(request):
    def get_room_list():
        current_day_schedules = filter_schedule_by_date(schedule, schedule_mode).exclude(pk=schedule.pk)
        return get_available_room_list(current_day_schedules)

    schedule_mode = request.GET.get('schedule_mode', None)
    schedule_id = request.GET.get('schedule_id', None)
    schedule = get_schedule(schedule_mode, schedule_id)

    result = {
        'teacher': {'id': schedule.teacher.pk, 'name': schedule.teacher.get_full_name()},
        'room': {'id': schedule.room.pk, 'name': schedule.room.get_full_name()},
        'subject': {'id': schedule.subject.pk, 'name': schedule.subject.name},
        'lesson_type': {'id': schedule.lesson_type.pk, 'name': schedule.lesson_type.name},
        'students': create_id_value_list_full_name(schedule.students.all()),
        'room_list': get_room_list(),
    }

    return result

def get_general_schedule(schedule_mode, start_date, end_date):
    if schedule_mode == 'set':
        return ScheduleSet.objects.filter(date__gte=start_date, date__lte=end_date)
    elif schedule_mode == 'regular':
        return ScheduleRegular.objects.all()

def get_date_from_schedule(schedule_mode, schedule, start_date):
    if schedule_mode == 'set':
        date = schedule.date
    elif schedule_mode == 'regular':
        date = start_date + datetime.timedelta(schedule.weekday)
        date = datetime.datetime.combine(date, schedule.time)
    return date


@ajax_request
@login_required
def ajax_load_admin_schedule(request, date):
    def get_schedule(schedule_mode, start_date, end_date):
        '''
            Returns a json of a dict of set schedule starting from Monday of the current week
        '''
        output = {}
        schedules = get_general_schedule(schedule_mode, start_date, end_date)

        schedules = schedules.filter(**filters)
        for schedule in schedules:
            date = get_date_from_schedule(schedule_mode, schedule, start_date)
            code = '%d_%s' % (schedule.room.pk, date.strftime(DATE_HOUR_CODE_FORMAT))
            output[code] = schedule.pk
        return output

    def get_teachers_filter():
        teachers = Teacher.objects.filter(**filters_subjects)
        return create_id_value_list_full_name(teachers)

    def get_students_filter():
        students = Student.objects.filter(**filters_subjects)
        return create_id_value_list_full_name(students)

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

    schedule_set = get_schedule('set', start_date, end_date)
    schedule_regular = get_schedule('regular', start_date, end_date)

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


@ajax_request
@login_required
def ajax_load_teacher_schedule(request, date):
    def get_schedule(schedule_mode, start_date, end_date):
        '''
            Returns a json of a dict of set schedule starting from Monday of the current week
        '''
        output = {}
        schedules = get_general_schedule(schedule_mode, start_date, end_date).filter(teacher__user=request.user)
        for schedule in schedules:
            date = get_date_from_schedule(schedule_mode, schedule, start_date)
            code = date.strftime(DATE_HOUR_CODE_FORMAT)
            output[code] = {'id': schedule.id, 'room': schedule.room.get_full_name()}
        return output

    start_date = get_start_date(parse_date(date))
    end_date = get_end_date(start_date)

    schedule_set = get_schedule('set', start_date, end_date)
    schedule_regular = get_schedule('regular', start_date, end_date)

    result = {
        'schedule_set': schedule_set,
        'schedule_regular': schedule_regular,
    }
    return result

def get_generic_hour_range():
    hours = range(settings.WORK_TIME[0], settings.WORK_TIME[1] + 1)
    hours = [str(x).zfill(2) for x in hours]
    return hours

def get_start_date_for_schedule(date):
    if date is not None:
        date = parse_date(date)
    else:
        date = datetime.date.today()
    return get_start_date(date)

def get_start_dates(start_date):
    return [
        start_date - datetime.timedelta(days=7),
        start_date,
        start_date + datetime.timedelta(days=7)
    ]

def get_date_range(start_date):
    'Returns a list of successive datetimes starting from Monday of the current week till Sunday'
    def daterange():
        dates = []
        for n in range(int ((end_date - start_date).days)):
            dates.append(start_date + datetime.timedelta(n))
        return dates
    end_date = get_end_date(start_date)
    return daterange()

def get_all_lesson_types():
    output = create_id_value_list(LessonType.objects.all())
    return json.dumps(output)

def get_all_subjects():
    output = create_id_value_list(Subject.objects.all())
    return json.dumps(output)

@render_to('admin-schedule.html')
@login_required
def admin_schedule(request, date=None):
    def initialize_session_values():
        if 'filters' not in request.session:
            request.session['filters'] = 'filters'
        if 'mode' not in request.session:
            request.session['mode'] = 0

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
        hours = get_generic_hour_range()
        return list(chunks(hours, 4))

    initialize_session_values()
    hours = get_hours_ranges()
    start_date = get_start_date_for_schedule(date)

    return {
        'hours': hours,
        'dates': get_date_range(start_date),
        'offices': get_offices(),
        'rooms': get_rooms(),
        'lesson_types': get_all_lesson_types(), #data for modal form
        'subjects': get_all_subjects(), #data for modal form
        'start_dates': get_start_dates(start_date),
    }

@render_to('teacher-schedule.html')
@login_required
def teacher_schedule(request, date=None):
    def initialize_session_values():
        if 'mode' not in request.session:
            request.session['mode'] = 0

    initialize_session_values()
    hours = get_generic_hour_range()
    start_date = get_start_date_for_schedule(date)

    return {
        'hours': hours,
        'dates': get_date_range(start_date),
        'start_dates': get_start_dates(start_date),
        'lesson_types': get_all_lesson_types(), #data for modal form
        'subjects': get_all_subjects(), #data for modal form
    }

@render_to('free-time.html')
@login_required
def free_time(request):
    hours = get_generic_hour_range()

    days = [x[1] for x in DAYS_OF_THE_WEEK]
    return {
        'hours': hours,
        'days': days,
    }