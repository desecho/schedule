from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'schedule.views.home'),

    url(r'^admin-schedule$', 'schedule.views.admin_schedule'),
    url(r'^admin-schedule/(?P<date>\d{2}-\d{2}-\d{4})$', 'schedule.views.admin_schedule'),
    url(r'^load-admin-schedule/(?P<date>\d{2}-\d{2}-\d{4})$', 'schedule.views.ajax_load_admin_schedule'),
    (r'^admin-schedule-modal', TemplateView.as_view(template_name='admin-schedule-modal.html')),
    url(r'^load-teachers$', 'schedule.views.ajax_load_teachers'),

    url(r'^teacher-schedule$', 'schedule.views.teacher_schedule'),
    url(r'^teacher-schedule/(?P<date>\d{2}-\d{2}-\d{4})$', 'schedule.views.teacher_schedule'),
    url(r'^load-teacher-schedule/(?P<date>\d{2}-\d{2}-\d{4})$', 'schedule.views.ajax_load_teacher_schedule'),
    (r'^teacher-schedule-modal', TemplateView.as_view(template_name='teacher-schedule-modal.html')),
    url(r'^demand-replacement$', 'schedule.views.ajax_demand_replacement'),
    url(r'^load-rooms$', 'schedule.views.ajax_load_rooms'),

    url(r'^load-students$', 'schedule.views.ajax_load_students'),
    url(r'^apply-settings$', 'schedule.views.ajax_apply_settings'),
    url(r'^save-schedule$', 'schedule.views.ajax_save_schedule'),
    url(r'^delete-schedule$', 'schedule.views.ajax_delete_schedule'),
    url(r'^load-hour-details$', 'schedule.views.ajax_load_hour_details'),
    url(r'^make-regular$', 'schedule.views.ajax_make_regular'),


    url(r'^free-time$', 'schedule.views.free_time'),
    url(r'^save-free-time$', 'schedule.views.ajax_save_free_time'),

    url(r'^register-student$', 'schedule.views.register_student'),
    url(r'^add-student$', 'schedule.views.add_student'),

    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout$', 'schedule.views.logout_view'),

    url(r'^admin', include(admin.site.urls)),
    url(r'^admin/doc', include('django.contrib.admindocs.urls')),

)
