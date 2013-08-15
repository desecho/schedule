# -*- coding: utf8 -*-
from django.db.models import SmallIntegerField
import models

class DayOfTheWeekField(SmallIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = models.DAYS_OF_THE_WEEK
        kwargs['max_length'] = 1
        super(DayOfTheWeekField,self).__init__(*args, **kwargs)
