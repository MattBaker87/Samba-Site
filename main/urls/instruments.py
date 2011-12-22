from django.conf.urls.defaults import include, patterns, url

from main.views import ActiveTemplateView
from main.views.instruments import ListInstruments, DetailInstrument, SignInBooking, InstrumentWriteNote, RemoveNote, AddInstrument, EditInstrument, DeleteInstrument, ResurrectInstrument, SignInInstrument
from main.models import Instrument


urlpatterns = patterns('sambasite.main.views.instruments',
    ###### Add, delete, undelete, edit, detail ######
    url(r'^add/$', AddInstrument.as_view(), name='instrument_add'),
    url(r'^delete/(?P<slug>[-\w]+)/$', DeleteInstrument.as_view(), name='instrument_delete'),
    url(r'^resurrect/(?P<slug>[-\w]+)/$', ResurrectInstrument.as_view(), name='instrument_resurrect'),
    url(r'^detail/(?P<slug>[-\w]+)/$', DetailInstrument.as_view(paginate_by=10), name='instrument_detail'),
    url(r'^edit/(?P<slug>[-\w]+)/$', EditInstrument.as_view(), name='instrument_edit'),
    
    ###### Sign in (sign out is on event page) ######
    url(r'^sign_in/(?P<slug>[-\w]+)/$', SignInInstrument.as_view(), name='instrument_signin_admin'),
    url(r'^sign_in/booking/(?P<booking_id>\d+)/$', SignInBooking.as_view(), name='instrument_booking_signin'),
    
    ###### Write notes ######
    url(r'^detail/(?P<slug>[-\w]+)/write_note/$', InstrumentWriteNote.as_view(), name='instrument_write_note'),
    url(r'^remove_note/(?P<pk>\d+)/$', RemoveNote.as_view(), name='remove_note'),
    
    ###### Lists #######
    url(r'^list/$', ActiveTemplateView.as_view(template_name='main/instruments/instrument_list.html'),
                                            name='instrument_list'),
    url(r'^list/mia/$', ActiveTemplateView.as_view(template_name='main/instruments/instrument_mia_list.html'),
                                            name='instrument_mia_list'),
    url(r'^list/deceased/$', ListInstruments.as_view(queryset=Instrument.objects.filter(is_removed=True),
                                        template_name='main/instruments/instrument_list_removed.html', paginate_by=None),
                                        name='instrument_list_removed'),
)