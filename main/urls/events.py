from django.conf.urls.defaults import include, patterns, url

from main.views.events import ListEvents, BookInstrument, CoordinateEvent, AddEvent, EditEvent
from main.models import Event


urlpatterns = patterns('sambasite.main.views.events',
    ####### Lists ########
    url(r'^upcoming/$', ListEvents.as_view(queryset=Event.objects.future_events(), paginate_by=10,
                                            template_name='main/events/event_list_upcoming.html'), name='events_upcoming'),
    url(r'^past/$', ListEvents.as_view(queryset=Event.objects.past_events(), paginate_by=10,
                                             template_name='main/events/event_list_past.html'), name='events_past'),
    
    ####### Add, edit, delete (note: detail view is in the URLs main section) #######
    url(r'^add/$', AddEvent.as_view(), name='event_add'),
    url(r'^(?P<slug>[-\w]+)/edit/$', EditEvent.as_view(), name='event_edit'),
    url(r'^(?P<slug>[-\w]+)/edit/players/$', 'edit_event_players', name='event_edit_players'),
    url(r'^(?P<slug>[-\w]+)/coordinate/$', CoordinateEvent.as_view(), name='event_coordinate'),
    url(r'^(?P<slug>[-\w]+)/cancel_coordinate/$', CoordinateEvent.as_view(), name='event_cancel_coordinate'),
    url(r'^(?P<slug>[-\w]+)/delete/$', 'delete_event', name='event_delete'),
    
    ####### Bookings #######
    url(r'^booking/sign_out_instrument/(?P<pk>\d+)/$', BookInstrument.as_view(), name='instrument_sign_out'),
    url(r'^booking/cancel_sign_out/(?P<pk>\d+)/$', BookInstrument.as_view(), name='cancel_sign_out'),
)