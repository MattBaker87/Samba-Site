from django.conf.urls.defaults import include, patterns, url

from main.views.events import DetailEvent

urlpatterns = patterns('',
    url(r'^$', 'sambasite.main.views.index', name='index'),
    url(r'^accounts/', include('sambasite.main.urls.accounts')),
    url(r'^events/', include('sambasite.main.urls.events')),
    url(r'^instruments/', include('sambasite.main.urls.instruments')),
    url(r'^admin/', include('sambasite.main.urls.admin')),
)

####### Vanity URLs for events. Note that this means there should be no other one-item path URLs #######
urlpatterns += patterns('sambasite.main.views.events',
    url(r'^(?P<slug>[-\w]+)/$', DetailEvent.as_view(), name='event_detail'),
)