from schedule.models import Subject, Teacher, Student, Office, Room
from django.contrib import admin
#from nested_inlines.admin import NestedModelAdmin, NestedTabularInline


# class AddressInline(NestedTabularInline):
#     model = Address
#     extra = 0


admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Office)
admin.site.register(Room)
