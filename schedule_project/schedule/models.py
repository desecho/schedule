# -*- coding: utf8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from annoying.fields import JSONField
import fields

DAYS_OF_THE_WEEK = (
    (0, u'Понедельник'),
    (1, u'Вторник'),
    (2, u'Среда'),
    (3, u'Четверг'),
    (4, u'Пятница'),
    (5, u'Суббота'),
    (6, u'Воскресенье'),
)

def get_weekday(n):
    weekdays = {x[0]: x[1] for x in DAYS_OF_THE_WEEK}
    return weekdays[n]

class Subject(models.Model):
    name = models.CharField('название', max_length=255)

    class Meta:
        verbose_name = 'предмет'
        verbose_name_plural = 'предметы'

    def __unicode__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, verbose_name='пользователь')
    free_time = JSONField('свободное время', default='{"0":[],"1":[],"2":[],"3":[],"4":[],"5":[],"6":[]}')
    subjects = models.ManyToManyField(Subject, verbose_name='предметы')

    class Meta:
        verbose_name = 'учитель'
        verbose_name_plural = 'учителя'

    def get_full_name(self):
        return self.user.get_full_name()

    def __unicode__(self):
        return self.get_full_name()


class Office(models.Model):
    name = models.CharField('название', max_length=255)

    class Meta:
        verbose_name = 'офис'
        verbose_name_plural = 'офисы'

    def __unicode__(self):
        return self.name


class Administrator(models.Model):
    user = models.OneToOneField(User, verbose_name='пользователь')
    office = models.ForeignKey(Office, verbose_name='офис')

    class Meta:
        verbose_name = 'администратор'
        verbose_name_plural = 'администраторы'

    def __unicode__(self):
        return self.user.get_full_name()


class Student(models.Model):
    name = models.CharField('имя', max_length=255)
    last_name = models.CharField('фамилия', max_length=255)
    middle_name = models.CharField('отчество', max_length=255)
    phone = models.CharField('телефон', max_length=255)
    birthday = models.DateField('дата рождения')
    email = models.EmailField('email', null=True, blank=True)
    subjects = models.ManyToManyField(Subject, verbose_name='предметы')
    time_preference_priority1 = JSONField('желаемое время. приоритет 1')
    time_preference_priority2 = JSONField('желаемое время. приоритет 2', null=True, blank=True)
    passport_number = models.IntegerField('паспорт, серия/номер', max_length=255)
    passport_authority = models.CharField('паспорт, выдан (кем)', max_length=255)
    passport_issued_date = models.DateField('паспорт, дата выдачи')
    passport_unit = models.CharField('паспорт, код подразделения', max_length=255)
    olympiad_participation_plans = models.BooleanField('планы участия в обл. или межд. олимпиадах, в КДР')
    foreign_trip_plans = models.BooleanField('планы поездок заграницу')

    class Meta:
        verbose_name = 'ученик'
        verbose_name_plural = 'ученики'

    def get_full_name(self):
        return '%s %s' % (self.name, self.last_name)

    def __unicode__(self):
        return self.get_full_name()


class Room(models.Model):
    name = models.CharField('название', max_length=255)
    office = models.ForeignKey(Office, verbose_name='офис')

    class Meta:
        verbose_name = 'кабинет'
        verbose_name_plural = 'кабинеты'

    def get_full_name(self):
        return '%s - %s' % (self.office.name, self.name)

    def __unicode__(self):
        return self.get_full_name()


class LessonType(models.Model):
    name = models.CharField('название', max_length=255)

    class Meta:
        verbose_name = 'тип урока'
        verbose_name_plural = 'типы урока'

    def __unicode__(self):
        return self.name


class ScheduleSet(models.Model):
    teacher = models.ForeignKey(Teacher, verbose_name='учитель')
    room = models.ForeignKey(Room, verbose_name='кабинет')
    lesson_type = models.ForeignKey(LessonType, verbose_name='тип урока')
    date = models.DateTimeField('дата/время')
    subject = models.ForeignKey(Subject, verbose_name='предмет')
    students = models.ManyToManyField(Student, verbose_name='ученики')
    replacement_demand = models.BooleanField('необходимость замены')

    class Meta:
        verbose_name = 'расписание установленное'
        verbose_name_plural = 'расписание установленное'

    def __unicode__(self):
        return '%s - %s - %s' % (self.date.strftime(settings.DATETIME_FORMAT), self.teacher.get_name(), self.room.get_full_name())


class ScheduleRegular(models.Model):
    teacher = models.ForeignKey(Teacher, verbose_name='учитель')
    room = models.ForeignKey(Room, verbose_name='кабинет')
    lesson_type = models.ForeignKey(LessonType, verbose_name='тип урока')
    weekday = fields.DayOfTheWeekField('день недели')
    time = models.TimeField('время')
    subject = models.ForeignKey(Subject, verbose_name='предмет')
    students = models.ManyToManyField(Student, verbose_name='ученики')

    class Meta:
        verbose_name = 'расписание постоянное'
        verbose_name_plural = 'расписание постоянное'

    def __unicode__(self):
        return '%s %s - %s' % (get_weekday(self.weekday), self.time.strftime(settings.TIME_FORMAT), self.teacher.get_name())
