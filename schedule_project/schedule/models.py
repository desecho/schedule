# -*- coding: utf8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
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
    user = models.OneToOneField(User, verbose_name='учитель')
    subjects = models.ManyToManyField(Subject, verbose_name='предметы')

    class Meta:
        verbose_name = 'учитель'
        verbose_name_plural = 'учителя'

    def get_name(self):
        return self.user.get_full_name()

    def __unicode__(self):
        return self.get_name()


class Student(models.Model):
    name = models.CharField('имя', max_length=255)
    subjects = models.ManyToManyField(Subject, verbose_name='предметы')

    class Meta:
        verbose_name = 'ученик'
        verbose_name_plural = 'ученики'

    def __unicode__(self):
        return self.name


class Office(models.Model):
    name = models.CharField('название', max_length=255)

    class Meta:
        verbose_name = 'офис'
        verbose_name_plural = 'офисы'

    def __unicode__(self):
        return self.name


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


class GroupType(models.Model):
    name = models.CharField('название', max_length=255)

    class Meta:
        verbose_name = 'тип группы'
        verbose_name_plural = 'типы группы'

    def __unicode__(self):
        return self.name


class ScheduleSet(models.Model):
    teacher = models.ForeignKey(Teacher, verbose_name='учитель')
    room = models.ForeignKey(Room, verbose_name='кабинет')
    group_type = models.ForeignKey(GroupType, verbose_name='тип группы')
    date = models.DateTimeField('дата/время')
    students = models.ManyToManyField(Student, verbose_name='ученики')

    class Meta:
        verbose_name = 'расписание установленное'
        verbose_name_plural = 'расписание установленное'

    def __unicode__(self):
        return '%s - %s - %s' % (self.date.strftime(settings.DATETIME_FORMAT), self.teacher.get_name(), self.room.get_full_name())

class ScheduleRegular(models.Model):
    teacher = models.ForeignKey(Teacher, verbose_name='учитель')
    room = models.ForeignKey(Room, verbose_name='кабинет')
    group_type = models.ForeignKey(GroupType, verbose_name='тип группы')
    weekday = fields.DayOfTheWeekField('день недели')
    time = models.TimeField('время')
    students = models.ManyToManyField(Student, verbose_name='ученики')

    class Meta:
        verbose_name = 'расписание постоянное'
        verbose_name_plural = 'расписание постоянное'

    def __unicode__(self):
        return '%s %s - %s' % (get_weekday(self.weekday), self.time.strftime(settings.TIME_FORMAT), self.teacher.get_name())


class FreeTime(models.Model):
    teacher = models.ForeignKey(Teacher, verbose_name='учитель')
    weekday = fields.DayOfTheWeekField('день недели')
    time = models.TimeField('время')

    class Meta:
        verbose_name = 'свободное время'
        verbose_name_plural = 'свободное время'

    def __unicode__(self):
        return '%s %s - %s' % (get_weekday(self.weekday), self.time.strftime(settings.TIME_FORMAT), self.teacher.get_name())

