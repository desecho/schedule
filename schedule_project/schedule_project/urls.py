from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^schedule_modal', TemplateView.as_view(template_name='schedule_modal.html')),
    url(r'^$', 'schedule.views.admin_schedule'),
    url(r'^teacher-schedule$', 'schedule.views.teacher_schedule'),
    url(r'^apply-settings$', 'schedule.views.ajax_apply_settings'),
    url(r'^save-schedule$', 'schedule.views.ajax_save_schedule'),
    url(r'^room-hour$', 'schedule.views.ajax_room_hour'),
    url(r'^delete-schedule$', 'schedule.views.ajax_delete_schedule'),
    url(r'^teachers-and-students$', 'schedule.views.ajax_teachers_and_students'),
    url(r'^(?P<date>\d{2}-\d{2}-\d{4})$', 'schedule.views.home'),
    url(r'^schedule/(?P<date>\d{2}-\d{2}-\d{4})$', 'schedule.views.ajax_schedule'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc', include('django.contrib.admindocs.urls')),

    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout$', 'schedule.views.logout_view'),

    # Uncomment the next line to enable the admin:
    url(r'^admin', include(admin.site.urls)),
)
