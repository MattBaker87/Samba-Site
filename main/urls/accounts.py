from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from sambasite.main.forms import LoginForm

from datetime import datetime, timedelta

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('sambasite.main.views.accounts',
    url(r'^signup/$', 'signup', name='signup'),
    url(r'^edit/$', 'edit_profile', name='edit_contact'),
    url(r'^profile/$', 'view_profile', name='profile'),
    url(r'^profile/(?P<slug>[-\w]+)/$', 'view_profile', name='view_profile'),
    url(r'^list/$', 'list_accounts', {'queryset_filter':lambda x:x.filter(last_login__gte=datetime.now()-timedelta(365), is_staff=False).order_by('userprofile__name'),
                                        'template_name': 'main/accounts/accounts_list.html'}, name='people'),
    url(r'^profile/(?P<slug>[-\w]+)/past_events/$', 'profile_past_events', name='profile_past_events'),
)


urlpatterns += patterns('django.views.generic',
    # url(r'^edit/$', 'simple.direct_to_template', {'template': 'main/accounts/edit_contact.html'},
    #                                                                         name='edit_contact'),
    url(r'^forgotten/$', 'simple.direct_to_template', {'template': 'main/accounts/forgotten.html'},
                                                                            name='forgotten'),
    url(r'^password/$', 'simple.direct_to_template', {'template': 'main/accounts/change_password.html'},
                                                                            name='change_password'),
)

urlpatterns += patterns('django.contrib',
    url(r'^login/$', 'auth.views.login', {'authentication_form': LoginForm, 'template_name': 'main/index.html'},
    													name='login'),
    url(r'^logout/$', 'auth.views.logout', {'next_page': reverse_lazy('index')}, name='logout'),
)