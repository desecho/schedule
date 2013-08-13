# -*- coding: utf8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType



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
    rooms = generic.GenericRelation('Room')

    class Meta:
        verbose_name = 'офис'
        verbose_name_plural = 'офисы'

    def __unicode__(self):
        return self.name


class Room(models.Model):
    name = models.CharField('название', max_length=255)
    #office = models.ForeignKey(Office, verbose_name='офис')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'кабинет'
        verbose_name_plural = 'кабинеты'

    def __unicode__(self):
        return self.name
