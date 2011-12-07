from django.conf.urls.defaults import include, patterns, url

urlpatterns = patterns('sambasite.main.views',
    # url(r'^$', 'index', name='index'),
)

urlpatterns += patterns('django.views.generic',
    url(r'^$', 'simple.direct_to_template', {'template': 'main/index.html'}, name='index'),
    url(r'^home$', 'simple.direct_to_template', {'template': 'main/home.html'}, name='home'),
    url(r'^accounts/signup$', 'simple.direct_to_template', {'template': 'main/accounts/signup.html'},
                                                                            name='signup'),
    url(r'^accounts/profile$', 'simple.direct_to_template', {'template': 'main/accounts/profile.html'},
                                                                            name='profile'),
    url(r'^accounts/contact$', 'simple.direct_to_template', {'template': 'main/accounts/edit_contact.html'},
                                                                            name='edit_contact'),
    url(r'^accounts/forgotten$', 'simple.direct_to_template', {'template': 'main/accounts/forgotten.html'},
                                                                            name='forgotten'),
    url(r'^accounts/password$', 'simple.direct_to_template', {'template': 'main/accounts/change_password.html'},
                                                                            name='change_password'),
    url(r'^events/upcoming$', 'simple.direct_to_template', {'template': 'main/events/event_list.html'},
                                                                            name='events_upcoming'),
    url(r'^events/past$', 'simple.direct_to_template', {'template': 'main/events/event_list.html'},
                                                                            name='events_past'),
    url(r'^events/yours$', 'simple.direct_to_template', {'template': 'main/events/event_list.html'},
                                                                            name='events_yours'),
    url(r'^events/detail$', 'simple.direct_to_template', {'template': 'main/events/event_detail.html'},
                                                                            name='event_detail'),
    url(r'^events/add$', 'simple.direct_to_template', {'template': 'main/events/event_add.html'},
                                                                            name='event_add'),
    url(r'^events/edit$', 'simple.direct_to_template', {'template': 'main/events/event_edit.html'},
                                                                            name='event_edit'),
    url(r'^instruments/list$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_list.html'},
                                                                            name='instrument_list'),
)

urlpatterns += patterns('django.contrib',
    # url(r'^accounts/login/$', 'auth.views.login', {'template_name': 'main/accounts/login.html'}, name='login'),
)