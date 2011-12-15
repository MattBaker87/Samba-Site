from django.conf.urls.defaults import include, patterns, url


urlpatterns = patterns('sambasite.main.views.instruments',
    url(r'^add/$', 'add_instrument', name='instrument_add'),
    url(r'^delete/(?P<slug>[-\w]+)/$', 'delete_instrument', name='instrument_delete'),
    url(r'^detail/(?P<slug>[-\w]+)/$', 'detail_instrument', {'paginate_by': 10}, name='instrument_detail'),
    url(r'^edit/(?P<slug>[-\w]+)/$', 'edit_instrument', name='instrument_edit'),
    url(r'^sign_in/booking/(?P<booking_id>\d+)/$', 'sign_in_booking', name='instrument_booking_signin'),
)

urlpatterns += patterns('sambasite.main.views',
    url(r'^list/$', 'login_direct_to_template', {'template': 'main/instruments/instrument_list.html'},
                                                                            name='instrument_list'),
    url(r'^list/mia/$', 'login_direct_to_template', {'template': 'main/instruments/instrument_mia_list.html'},
                                                                            name='instrument_mia_list'),
)