from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'picostack.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', RedirectView.as_view(url='/instances', permanent=False), name='instances'),
    url(r'^instances/', 'picostack.vms.views.manage_instances', name='instances'),
    url(r'^admin/', include(admin.site.urls)),
)
