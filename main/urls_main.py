from django.conf.urls.defaults import include, patterns, url

urlpatterns = patterns('',
    url(r'^$', 'sambasite.main.views.index', name='index'),
    url(r'^accounts/', include('sambasite.main.urls.accounts')),
    url(r'^events/', include('sambasite.main.urls.events')),
    url(r'^instruments/', include('sambasite.main.urls.instruments')),
    url(r'^admin/', include('sambasite.main.urls.admin')),
)

urlpatterns += patterns('django.views.generic',
    url(r'^home/$', 'simple.direct_to_template', {'template': 'main/home.html'}, name='home'),
)