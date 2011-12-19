from django.conf.urls.defaults import include, patterns, url


urlpatterns = patterns('sambasite.main.views.instruments',
    url(r'^add/$', 'add_instrument', name='instrument_add'),
    url(r'^delete/(?P<slug>[-\w]+)/$', 'delete_instrument', name='instrument_delete'),
    url(r'^resurrect/(?P<slug>[-\w]+)/$', 'resurrect_instrument', name='instrument_resurrect'),
    url(r'^detail/(?P<slug>[-\w]+)/$', 'detail_instrument', {'paginate_by': 10}, name='instrument_detail'),
    url(r'^detail/(?P<slug>[-\w]+)/write_note/$', 'instrument_write_note', name='instrument_write_note'),
    url(r'^edit/(?P<slug>[-\w]+)/$', 'edit_instrument', name='instrument_edit'),
    url(r'^sign_in/(?P<slug>[-\w]+)/$', 'sign_in_instrument', name='instrument_signin_admin'),
    url(r'^sign_in/booking/(?P<booking_id>\d+)/$', 'sign_in_booking', name='instrument_booking_signin'),
    url(r'^remove_note/(?P<note_id>\d+)/$', 'remove_note', name='remove_note'),
    url(r'^list/deceased/$', 'list_instruments', {'queryset_filter': lambda x:x.filter(is_removed=True),
                                        'template_name': 'main/instruments/instrument_list_removed.html', 'paginate_by':10},
                                        name='instrument_list_removed'),
)

urlpatterns += patterns('sambasite.main.views',
    url(r'^list/$', 'login_direct_to_template', {'template': 'main/instruments/instrument_list.html'},
                                                                            name='instrument_list'),
    url(r'^list/mia/$', 'login_direct_to_template', {'template': 'main/instruments/instrument_mia_list.html'},
                                                                            name='instrument_mia_list'),
)