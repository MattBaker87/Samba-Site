from django.conf.urls.defaults import include, patterns, url


urlpatterns = patterns('sambasite.main.views.events',
)

urlpatterns += patterns('django.views.generic',
    url(r'^upcoming/$', 'simple.direct_to_template', {'template': 'main/events/event_list.html'},
                                                                            name='events_upcoming'),
    url(r'^past/$', 'simple.direct_to_template', {'template': 'main/events/event_list.html'},
                                                                            name='events_past'),
    url(r'^yours/$', 'simple.direct_to_template', {'template': 'main/events/event_list.html'},
                                                                            name='events_yours'),
    url(r'^detail/$', 'simple.direct_to_template', {'template': 'main/events/event_detail.html'},
                                                                            name='event_detail'),
    url(r'^add/$', 'simple.direct_to_template', {'template': 'main/events/event_add.html'},
                                                                            name='event_add'),
    url(r'^edit/$', 'simple.direct_to_template', {'template': 'main/events/event_edit.html'},
                                                                            name='event_edit'),
    url(r'^delete/$', 'simple.direct_to_template', {'template': 'main/events/event_delete.html'},
                                                                            name='event_delete'),
)

urlpatterns += patterns('django.contrib',
)