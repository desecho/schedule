from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'schedule.views.home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$', 'schedule.views.logout_view'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
