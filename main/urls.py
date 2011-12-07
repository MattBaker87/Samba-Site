from django.conf.urls.defaults import include, patterns, url

urlpatterns = patterns('sambasite.main.views',
    # url(r'^$', 'index', name='index'),
)

urlpatterns += patterns('django.views.generic',
    url(r'^$', 'simple.direct_to_template', {'template': 'main/index.html'}, name='index'),
)

urlpatterns += patterns('django.contrib',
    # url(r'^accounts/login/$', 'auth.views.login', {'template_name': 'main/accounts/login.html'}, name='login'),
)