from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^schedule_modal', TemplateView.as_view(template_name='schedule_modal.html')),
    url(r'^$', 'schedule.views.home'),
    url(r'^apply-settings$', 'schedule.views.ajax_apply_settings'),
    url(r'^(?P<date>\d{2}-\d{2}-\d{4})$', 'schedule.views.home'),
    url(r'^schedule/(?P<date>\d{2}-\d{2}-\d{4})$', 'schedule.views.schedule'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc', include('django.contrib.admindocs.urls')),

    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout$', 'schedule.views.logout_view'),

    # Uncomment the next line to enable the admin:
    url(r'^admin', include(admin.site.urls)),
)
