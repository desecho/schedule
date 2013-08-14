# -*- coding: utf8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Subject(models.Model):
    name = models.CharField('название', max_length=255)

    class Meta:
        verbose_name = 'предмет'
        verbose_name_plural = 'предметы'

    def __unicode__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField('имя', max_length=255)
    subjects = models.ManyToManyField(Subject, verbose_name='предметы')

    class Meta:
        verbose_name = 'учитель'
        verbose_name_plural = 'учителя'

    def __unicode__(self):
        return self.name


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

    def __unicode__(self):
        return self.name


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
        return self.teacher.name + ' ' + self.room.name


class ScheduleRegular(models.Model):
    teacher = models.ForeignKey(Teacher, verbose_name='учитель')
    room = models.ForeignKey(Room, verbose_name='кабинет')
    group_type = models.ForeignKey(GroupType, verbose_name='тип группы')
    date = models.DateTimeField('дата/время')
    students = models.ManyToManyField(Student, verbose_name='ученики')

    class Meta:
        verbose_name = 'расписание постоянное'
        verbose_name_plural = 'расписание постоянное'

    def __unicode__(self):
        return self.teacher.name + ' ' + self.room.name

