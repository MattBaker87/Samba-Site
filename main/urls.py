from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from forms import LoginForm

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('sambasite.main.views',
    url(r'^$', 'index', name='index'),
    url(r'^accounts/signup$', 'signup', name='signup'),
)

urlpatterns += patterns('django.views.generic',
    url(r'^home$', 'simple.direct_to_template', {'template': 'main/home.html'}, name='home'),
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
    url(r'^events/delete$', 'simple.direct_to_template', {'template': 'main/events/event_delete.html'},
                                                                            name='event_delete'),
    url(r'^instruments/list$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_list.html'},
                                                                            name='instrument_list'),
    url(r'^instruments/signin$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_signin.html'},
                                                                            name='instrument_signin'),
    url(r'^instruments/detail$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_detail.html'},
                                                                            name='instrument_detail'),
    url(r'^instruments/add$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_add.html'},
                                                                            name='instrument_add'),
    url(r'^instruments/delete$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_delete.html'},
                                                                            name='instrument_delete'),
    url(r'^instruments/edit$', 'simple.direct_to_template', {'template': 'main/instruments/instrument_edit.html'},
                                                                            name='instrument_edit'),
)

urlpatterns += patterns('django.contrib',
    url(r'^accounts/login/$', 'auth.views.login', {'authentication_form': LoginForm, 'template_name': 'main/index.html'},
    													name='login'),
    url(r'^accounts/logout/$', 'auth.views.logout', {'next_page': reverse_lazy('index')}, name='logout'),
)