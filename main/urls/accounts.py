from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from sambasite.main.forms import LoginForm

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('sambasite.main.views.accounts',
    url(r'^signup$', 'signup', name='signup'),
)

urlpatterns += patterns('django.views.generic',
    url(r'^profile/$', 'simple.direct_to_template', {'template': 'main/accounts/profile.html'},
                                                                            name='profile'),
    url(r'^contact/$', 'simple.direct_to_template', {'template': 'main/accounts/edit_contact.html'},
                                                                            name='edit_contact'),
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