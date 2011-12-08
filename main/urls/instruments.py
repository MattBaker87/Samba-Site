from django.conf.urls.defaults import include, patterns, url


urlpatterns = patterns('sambasite.main.views.instruments',
)

urlpatterns += patterns('django.views.generic',
    url(r'^list/$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_list.html'},
                                                                            name='instrument_list'),
    url(r'^signin/$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_signin.html'},
                                                                            name='instrument_signin'),
    url(r'^detail/$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_detail.html'},
                                                                            name='instrument_detail'),
    url(r'^add/$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_add.html'},
                                                                            name='instrument_add'),
    url(r'^delete/$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_delete.html'},
                                                                            name='instrument_delete'),
    url(r'^edit/$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_edit.html'},
                                                                            name='instrument_edit'),
)

urlpatterns += patterns('django.contrib',
)