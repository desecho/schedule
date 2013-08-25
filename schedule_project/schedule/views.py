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

DATE_CODE_FORMAT = '%d%m%Y'
DATE_HOUR_CODE_FORMAT = DATE_CODE_FORMAT + '_%H'

def create_id_value_list(input):
    '''
        Keyword arguments:
            input -- QuerySet

        Returns List containing Dict
    '''
    return [{'id': x.pk, 'name': x.name} for x in input]

def create_id_value_list_full_name(input):
    '''
        Keyword arguments:
            input -- QuerySet

        Returns List containing Dict
    '''
    return [{'id': x.pk, 'name': x.get_full_name()} for x in input]

def parse_date(date):
    '''
        Keyword arguments:
            date -- String

        Returns date
    '''
    return datetime.datetime.strptime(date, '%d-%m-%Y').date()

def parse_datetime(date):
    '''
        Keyword arguments:
            date -- String

        Returns datetime
    '''
    return datetime.datetime.strptime(date, DATE_HOUR_CODE_FORMAT)

def get_start_date(date):
    '''
        Returns the datetime of Monday of the date's week

        Keyword arguments:
            date -- datetime
    '''
    return date - datetime.timedelta(days=date.weekday())

def get_end_date(start_date):
    '''
        Returns the datetime of 1 week ahead from the start_date

        Keyword arguments:
            start_date -- datetime
    '''
    return start_date + relativedelta(weeks=1)

def get_schedule(schedule_mode, schedule_id):
    '''
        Keyword arguments:
            schedule_mode -- String
            schedule_id - String

        Returns Schedule
    '''
    if schedule_mode == '0':
        schedule = ScheduleSet
    elif schedule_mode == '1':
        schedule = ScheduleRegular
    return schedule.objects.get(pk=schedule_id)

def filter_schedules_by_date_from_schedule(schedule, schedule_mode):
    '''
        Returns Schedules QuerySet filtered by date

        Keyword arguments:
            schedule -- Schedule
            schedule_mode -- String
    '''
    if schedule_mode == '0':
        filters = {'date': schedule.date}
        schedules = ScheduleSet
    elif schedule_mode == '1':
        filters = {
            'weekday': schedule.weekday,
            'time': schedule.time,
        }
        schedules = ScheduleRegular
    return schedules.objects.filter(**filters)

def get_schedule_and_filters(schedule_mode, date):
    '''
        Returns Tuple (Schedule, Dict) - (Schedule, date filters)

        Keyword arguments:
            schedule_mode -- String
            date -- datetime
    '''
    if schedule_mode == '0':
        schedule = ScheduleSet
        filters = {'date': date}
    elif schedule_mode == '1':
        schedule = ScheduleRegular
        filters = {
            'weekday': date.weekday,
            'time': date.time,
        }
    return (schedule, filters)

def filter_schedules_by_date(schedule_mode, date):
    '''
        Returns Schedules filtered by date

        Keyword arguments:
            schedule_mode -- String
            date -- datetime
    '''
    schedule, filters = get_schedule_and_filters(schedule_mode, date)
    return schedule.objects.filter(**filters)

def has_conflicts_on_adding(type, schedule, filters):
    '''
        Tests if the Schedule already exists. Includes 3 types of checks:
            self - Checks if the schedule has been already created
            room - Checks if the room is not busy at that day
            teacher - Checks if the teacher is not busy at that day

        Keyword arguments:
            type -- String
            schedule -- Schedule (general object)
            filters -- Dict

        Returns Boolean
    '''
    if type != 'self':
        if type == 'room':
            parameter_to_remove = 'teacher'
        if type == 'teacher':
            parameter_to_remove = 'room'
        del filters['subject']
        del filters['lesson_type']
        del filters[parameter_to_remove]
    n = schedule.objects.filter(**filters).count()
    return n != 0

def parse_room_hour_code(room_hour_code):
    '''
        Keyword arguments:
            room_hour_code -- String

        Returns (String, datetime) - (Room id, date)
    '''
    match = re.match('(\d+)_(.+)', room_hour_code)
    room_id = match.group(1)
    date = parse_datetime(match.group(2))
    return (room_id, date)

def logout_view(request):
    logout(request)
    return redirect('/login')

def ajax_apply_settings(request):
    'Saves settings into session'
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'settings' in POST:
            session_settings = json.loads(POST.get('settings'))
            for setting in session_settings:
                request.session[setting] = json.dumps(session_settings[setting])
    return HttpResponse()

@ajax_request
@login_required
def ajax_save_schedule(request):
    'Returns String - Schedule id'
    def has_conflicts_on_changing(type):
        '''
            Tests if the Schedule already exists. Includes 3 types of checks:
                room - Checks if the room is not busy at that day
                teacher - Checks if the teacher is not busy at that day

            Keyword arguments:
                type -- String

            Returns Boolean
        '''
        schedule_filter = filter_schedules_by_date_from_schedule(schedule, schedule_mode)
        if type == 'room':
            filters= {type: room}
        if type == 'teacher':
            filters= {type: teacher}
        n = schedule_filter.filter(**filters).exclude(pk=schedule.pk).count()
        return n != 0

    def get_teacher():
        'Returns Teacher'
        teacher = POST.get('teacher', None)
        if teacher is None:
            filters = {'user': request.user}
        else:
            filters = {'pk': teacher}
        return Teacher.objects.get(**filters)

    def get_students():
        'Returns Students'
        return Student.objects.filter(pk__in=json.loads(POST.get('students')))

    def get_room_and_date():
        room_hour_code = POST.get('room_hour_code', None)
        hour_code = POST.get('hour_code', None)
        if room_hour_code is not None:
            room_id, date = parse_room_hour_code(room_hour_code)
            room = Room.objects.get(pk=room_id)
        else:
            date = parse_datetime(hour_code)
        return (room, date)

    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        schedule_mode = POST.get('schedule_mode')
        room = POST.get('room', None)

        subject = Subject.objects.get(pk=POST.get('subject'))
        lesson_type = LessonType.objects.get(pk=POST.get('lesson_type'))
        teacher = get_teacher()

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
                if has_conflicts_on_changing('room'):
                    return {'success': False, 'error': 'Кабинет на это время уже занят'}
            if has_conflicts_on_changing('teacher'):
                return {'success': False, 'error': 'Учитель в это время занят'}
        else:
            room, date = get_room_and_date()
            filters = {
                'subject': subject,
                'lesson_type': lesson_type,
                'teacher': teacher,
                'room': room,
            }
            schedule, date_filters = get_schedule_and_filters(schedule_mode, date)
            filters.update(date_filters)
            if has_conflicts_on_adding('room', schedule, dict(filters)):
                return {'success': False, 'error': 'Кабинет на это время уже занят'}
            if has_conflicts_on_adding('teacher', schedule, dict(filters)):
                return {'success': False, 'error': 'Учитель в это время занят'}

            schedule = schedule(**filters)

        schedule.save()
        schedule.students = get_students()
    return {'success': True, 'schedule_id': schedule.pk}

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
def ajax_load_teachers(request):
    'Returns a List of teacher names'
    def get_busy_teachers():
        def get_date():
            room_hour_code = request.GET.get('room_hour_code', None)
            room_and_date = parse_room_hour_code(room_hour_code)
            return room_and_date[1]

        schedule_mode = request.GET.get('schedule_mode', None)
        schedule_id = request.GET.get('schedule_id', None)
        schedules = filter_schedules_by_date(schedule_mode, get_date())
        if schedule_id is not None:
            schedules = schedules.exclude(pk=schedule_id)
        busy_teachers = schedules.values_list('teacher')
        return [x[0] for x in busy_teachers]

    subject_id = request.GET.get('subject_id', None)
    busy_teachers = get_busy_teachers()
    teachers = Teacher.objects.filter(subjects__pk=subject_id)
    teachers = [x for x in create_id_value_list_full_name(teachers) if x['id'] not in busy_teachers]

    result = {
        'teachers': teachers,
    }
    return result

@ajax_request
@login_required
def ajax_load_students(request):
    'Returns a List of student names'
    subject_id = request.GET.get('subject_id', None)
    students = create_id_value_list_full_name(Student.objects.filter(subjects__pk=subject_id))
    result = {
        'students': students,
    }
    return result


def get_available_rooms(busy_schedules):
    '''
        Returns a List of available rooms.

        Keyword arguments:
            busy_schedules -- Schedule QuerySet
    '''
    def get_busy_rooms(busy_schedules):
        busy_rooms = busy_schedules.values_list('room')
        return [x[0] for x in busy_rooms]
    busy_rooms = get_busy_rooms(busy_schedules)
    return [x for x in create_id_value_list_full_name(Room.objects.all()) if x['id'] not in busy_rooms]

@ajax_request
@login_required
def ajax_load_rooms(request):
    'Returns a List of available rooms.'
    schedule_mode = request.GET.get('schedule_mode', None)
    hour_code = request.GET.get('hour_code', None)
    date = parse_datetime(hour_code)
    busy_schedules = filter_schedules_by_date(schedule_mode, date)
    return get_available_rooms(busy_schedules)

@ajax_request
@login_required
def ajax_load_hour_details(request):
    '''
        Returns dict of
        - dict with teacher id and name,
        - dict with room id and name,
        - dict with subject id and name,
        - dict with lesson_type id and name,
        - dict with students ids and names,
        - list of available rooms
    '''
    def get_rooms():
        'Returns a List of available rooms.'
        busy_schedules = filter_schedules_by_date_from_schedule(schedule, schedule_mode).exclude(pk=schedule.pk)
        return get_available_rooms(busy_schedules)

    schedule_mode = request.GET.get('schedule_mode', None)
    schedule_id = request.GET.get('schedule_id', None)
    schedule = get_schedule(schedule_mode, schedule_id)

    result = {
        'teacher': {'id': schedule.teacher.pk, 'name': schedule.teacher.get_full_name()},
        'room': {'id': schedule.room.pk, 'name': schedule.room.get_full_name()},
        'subject': {'id': schedule.subject.pk, 'name': schedule.subject.name},
        'lesson_type': {'id': schedule.lesson_type.pk, 'name': schedule.lesson_type.name},
        'students': create_id_value_list_full_name(schedule.students.all()),
        'rooms': get_rooms(),
    }

    return result

def get_all_schedules(schedule_mode, start_date, end_date):
    '''
        Returns Schedule QuerySet

        Keyword arguments:
            schedule_mode -- String
            start_date -- datetime
            end_date -- datetime
    '''
    if schedule_mode == 'set':
        return ScheduleSet.objects.filter(date__gte=start_date, date__lte=end_date)
    elif schedule_mode == 'regular':
        return ScheduleRegular.objects.all()

def get_date_from_schedule(schedule_mode, schedule, start_date):
    '''
        Returns datetime

        Keyword arguments:
            schedule_mode -- String
            schedule -- Schedule
            start_date -- datetime
    '''
    if schedule_mode == 'set':
        date = schedule.date
    elif schedule_mode == 'regular':
        date = start_date + datetime.timedelta(schedule.weekday)
        date = datetime.datetime.combine(date, schedule.time)
    return date

#2do continue commenting
@ajax_request
@login_required
def ajax_load_admin_schedule(request, date):
    def get_filtered_schedules(schedule_mode, start_date, end_date):
        schedules = get_all_schedules(schedule_mode, start_date, end_date)
        return schedules.filter(**filters)

    def get_schedule(schedule_mode, start_date, end_date, replacements=False):
        '''
            Returns a dict of set schedule starting from Monday of the current week
        '''
        output = {}

        schedules = get_filtered_schedules(schedule_mode, start_date, end_date)

        if replacements:
            schedules = schedules.filter(replacement_demand=True)
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

    def get_custom_free_time(free_time):
        output = []
        rooms = Room.objects.all()
        for day in free_time:
            for hour in free_time[day]:
                for room in rooms:
                    date = start_date + datetime.timedelta(days=int(day))
                    code = '%d_%s_%s' % (room.pk, date.strftime(DATE_CODE_FORMAT), hour)
                    output.append(code)
        return output

    teacher = request.GET.get('teacher', '')
    student = request.GET.get('student', '')
    subject = request.GET.get('subject', '')
    lesson_type = request.GET.get('lesson_type', '')
    filters = {}
    filters_subjects = {}
    free_time = None

    start_date = get_start_date(parse_date(date))
    end_date = get_end_date(start_date)

    if teacher != '':
        filters['teacher__pk'] = teacher
        free_time = get_custom_free_time(Teacher.objects.get(pk=teacher).free_time)
    if lesson_type != '':
        filters['lesson_type__pk'] = lesson_type
    if student != '':
        filters['students__pk'] = student
    if subject != '':
        filters['subject__pk'] = subject
        filters_subjects['subjects__pk'] = subject

    result = {
        'schedule_set': get_schedule('set', start_date, end_date),
        'schedule_regular': get_schedule('regular', start_date, end_date),
        'schedule_replacements': get_schedule('set', start_date, end_date, True),
        'teachers': get_teachers_filter(),
        'students': get_students_filter(),
        'subjects': get_subjects_filter(),
        'lesson_types': get_lesson_types_filter(),
        'free_time': free_time,
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
        schedules = get_all_schedules(schedule_mode, start_date, end_date).filter(teacher__user=request.user)
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

def initialize_mode_setting(session):
    if 'mode' not in session:
        session['mode'] = 0

@render_to('admin-schedule.html')
@login_required
def admin_schedule(request, date=None):
    def initialize_settings():
        if 'filters' not in request.session:
            request.session['filters'] = {}
        initialize_mode_setting(request.session)

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

    initialize_settings()
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
    initialize_mode_setting(request.session)
    hours = get_generic_hour_range()
    start_date = get_start_date_for_schedule(date)

    return {
        'hours': hours,
        'dates': get_date_range(start_date),
        'start_dates': get_start_dates(start_date),
        'lesson_types': get_all_lesson_types(), #data for modal form
        'subjects': get_all_subjects(), #data for modal form
    }

@ajax_request
@login_required
def ajax_load_free_time(request):
    free_time = Teacher.objects.get(user=request.user).free_time
    return {'time': free_time}


@ajax_request
@login_required
def ajax_save_free_time(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'free_time' in POST:
            free_time = POST.get('free_time')
            teacher = Teacher.objects.get(user=request.user)
            teacher.free_time = free_time
            teacher.save()
    return HttpResponse()

@ajax_request
@login_required
def ajax_make_regular(request):
    schedule_id = request.GET.get('schedule_id', None)
    schedule = ScheduleSet.objects.get(pk=schedule_id)
    data = {
        'teacher': schedule.teacher,
        'subject': schedule.subject,
        'lesson_type': schedule.lesson_type,
        'room': schedule.room,
        'weekday': schedule.date.weekday(),
        'time': schedule.date.time()
    }
    schedule_regular = ScheduleRegular
    if has_conflicts_on_adding('self', schedule_regular, dict(data)):
        return {'success': False, 'error': 'Этот урок уже назначен постоянным'}
    if has_conflicts_on_adding('room', schedule_regular, dict(data)):
        return {'success': False, 'error': 'Кабинет на это время уже занят'}
    if has_conflicts_on_adding('teacher', schedule_regular, dict(data)):
        return {'success': False, 'error': 'Учитель в это время занят'}
    schedule_regular = schedule_regular(**data)
    schedule_regular.save()
    schedule_regular.students = schedule.students.all()
    return {'success': True}

@render_to('free-time.html')
@login_required
def free_time(request):
    hours = get_generic_hour_range()

    return {
        'hours': hours,
        'days': DAYS_OF_THE_WEEK,
    }

@login_required
def ajax_demand_replacement(request):
    schedule_id = request.GET.get('schedule_id', None)
    schedule = ScheduleSet.objects.get(pk=schedule_id)
    schedule.replacement_demand = True
    schedule.save()
    return HttpResponse()