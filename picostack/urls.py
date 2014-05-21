from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/instances', permanent=False), name='instances'),
    url(r'^list_instances/', 'picostack.vms.views.list_instances', name='instances'),
    url(r'^instances/', 'picostack.vms.views.manage_instances', name='instances'),
    url(r'^logout/', 'picostack.vms.views.logout_view', name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'frontend_registration/login.html'}),
)
