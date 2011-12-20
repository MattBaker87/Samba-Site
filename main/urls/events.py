from django.conf.urls.defaults import include, patterns, url


urlpatterns = patterns('sambasite.main.views.events',
    ####### Lists ########
    url(r'^upcoming/$', 'list_events', {'queryset_filter': lambda x:x.future_events(),
                                        'template_name': 'main/events/event_list_upcoming.html', 'paginate_by':10},
                                        name='events_upcoming'),
    url(r'^past/$', 'list_events', {'queryset_filter': lambda x:x.past_events(),
                                        'template_name': 'main/events/event_list_past.html', 'paginate_by':10},
                                        name='events_past'),
    
    ####### Add, edit, delete (note: detail view is in the URLs main section) #######
    url(r'^add/$', 'add_event', name='event_add'),
    url(r'^(?P<slug>[-\w]+)/edit/$', 'edit_event', name='event_edit'),
    url(r'^(?P<slug>[-\w]+)/edit/players/$', 'edit_event_players', name='event_edit_players'),
    url(r'^(?P<slug>[-\w]+)/coordinate/$', 'coordinate_event', name='event_coordinate'),
    url(r'^(?P<slug>[-\w]+)/cancel_coordinate/$', 'cancel_coordinate_event', name='event_cancel_coordinate'),
    url(r'^(?P<slug>[-\w]+)/delete/$', 'delete_event', name='event_delete'),
    
    ####### Bookings #######
    url(r'^booking/sign_out_instrument/(?P<booking_id>\d+)/$', 'sign_out_instrument', name='instrument_sign_out'),
    url(r'^booking/cancel_sign_out/(?P<booking_id>\d+)/$', 'cancel_sign_out', name='cancel_sign_out'),
)