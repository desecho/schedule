# -*- coding: utf8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from annoying.fields import JSONField
import fields

DAYS_OF_THE_WEEK = (
    (0, u'Monday'),
    (1, u'Tuesday'),
    (2, u'Wednesday'),
    (3, u'Thursday'),
    (4, u'Friday'),
    (5, u'Saturday'),
    (6, u'Sunday'),
)

EMPTY_FREE_TIME_JSON = '{"0":[],"1":[],"2":[],"3":[],"4":[],"5":[],"6":[]}'


def get_weekday(n):
    weekdays = {x[0]: x[1] for x in DAYS_OF_THE_WEEK}
    return weekdays[n]


class Subject(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'subject'

    def __unicode__(self):
        return self.name


class Office(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'office'

    def __unicode__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    free_time = JSONField(default=EMPTY_FREE_TIME_JSON)
    subjects = models.ManyToManyField(Subject)
    office = models.ForeignKey(Office)
    skype_availability = models.BooleanField()
    translation_availability = models.BooleanField()

    class Meta:
        verbose_name = 'teacher'

    def get_full_name(self):
        return '%s %s' % (self.last_name, self.name)

    def __unicode__(self):
        return self.get_full_name()


class Administrator(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    office = models.ForeignKey(Office)

    class Meta:
        verbose_name = 'administrator'

    def get_full_name(self):
        return '%s %s' % (self.last_name, self.name)

    def __unicode__(self):
        return self.get_full_name()


class Student(models.Model):
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    parents_phone = models.CharField("parent's phone", max_length=255, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    birthday = models.DateField()
    free_time = JSONField(default=EMPTY_FREE_TIME_JSON)
    level = models.PositiveSmallIntegerField(default=0)
    subjects = models.ManyToManyField(Subject)
    offices = models.ManyToManyField(Office)
    foreign_trip_plans = models.BooleanField('trip plans')
    registration_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'student'

    def get_full_name(self):
        return '%s %s' % (self.last_name, self.name)

    def __unicode__(self):
        return self.get_full_name()


class Room(models.Model):
    name = models.CharField(max_length=255)
    office = models.ForeignKey(Office)

    class Meta:
        verbose_name = 'room'

    def get_full_name(self):
        return '%s - %s' % (self.office.name, self.name)

    def __unicode__(self):
        return self.get_full_name()


class LessonType(models.Model):
    name = models.CharField(max_length=255)
    price = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'lesson type'

    def __unicode__(self):
        return self.name


class ScheduleSet(models.Model):
    teacher = models.ForeignKey(Teacher)
    room = models.ForeignKey(Room)
    lesson_type = models.ForeignKey(LessonType)
    date = models.DateTimeField('date/time')
    subject = models.ForeignKey(Subject)
    students = models.ManyToManyField(Student)
    replacement_demand = models.BooleanField()

    class Meta:
        verbose_name = 'set schedule'

    def __unicode__(self):
        return '%s - %s - %s' % (self.date.strftime(settings.DATETIME_FORMAT), self.teacher.get_full_name(), self.room.get_full_name())

    # def save(self, *args, **kwargs):
    #     super(ScheduleSet, self).save(*args, **kwargs)


class ScheduleRegular(models.Model):
    teacher = models.ForeignKey(Teacher)
    room = models.ForeignKey(Room)
    lesson_type = models.ForeignKey(LessonType)
    weekday = fields.DayOfTheWeekField()
    time = models.TimeField()
    subject = models.ForeignKey(Subject)
    students = models.ManyToManyField(Student)

    class Meta:
        verbose_name = 'regular schedule'

    def __unicode__(self):
        return '%s %s - %s' % (get_weekday(self.weekday), self.time.strftime(settings.TIME_FORMAT), self.teacher.get_full_name())


from django.dispatch import receiver
from django.db.models.signals import pre_save


@receiver(pre_save, sender=ScheduleSet)
def remove_replacement_demand_when_replacement_occurs(sender, instance, **kwargs):
    if instance.replacement_demand:
        schedule = ScheduleSet.objects.get(pk=instance.pk)
        if not schedule.teacher == instance.teacher:
            instance.replacement_demand = False
