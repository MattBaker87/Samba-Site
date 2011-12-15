from django.conf.urls.defaults import include, patterns, url


urlpatterns = patterns('sambasite.main.views.events',
    url(r'^add/$', 'add_event', name='event_add'),
    url(r'^delete/(?P<slug>[-\w]+)/$', 'delete_event', name='event_delete'),
    url(r'^detail/(?P<slug>[-\w]+)/$', 'detail_event', name='event_detail'),
    url(r'^edit/(?P<slug>[-\w]+)/$', 'edit_event', name='event_edit'),
    url(r'^sign_out_instrument/(?P<booking_id>\d+)/$', 'sign_out_instrument', name='instrument_sign_out'),
    url(r'^cancel_sign_out/(?P<booking_id>\d+)/$', 'cancel_sign_out', name='cancel_sign_out'),
    url(r'^upcoming/$', 'list_events', {'queryset_filter': lambda x:x.future_events(),
                                        'template_name': 'main/events/event_list_upcoming.html', 'paginate_by':10},
                                        name='events_upcoming'),
    url(r'^past/$', 'list_events', {'queryset_filter': lambda x:x.past_events(),
                                        'template_name': 'main/events/event_list_past.html', 'paginate_by':10},
                                        name='events_past'),
)

urlpatterns += patterns('django.views.generic',
)

urlpatterns += patterns('django.contrib',
)