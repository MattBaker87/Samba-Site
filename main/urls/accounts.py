from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from sambasite.main.forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm

from datetime import datetime, timedelta

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('sambasite.main.views.accounts',
    url(r'^signup/$', 'signup', name='signup'),
    url(r'^edit/$', 'edit_profile', name='edit_contact'),
    url(r'^profile/$', 'view_profile', name='profile'),
    url(r'^profile/(?P<slug>[-\w]+)/$', 'view_profile', name='view_profile'),
    url(r'^list/$', 'list_accounts', {'queryset_filter':lambda x:x.filter(last_login__gte=datetime.now()-timedelta(365)).order_by('userprofile__name'),
                                        'template_name': 'main/accounts/accounts_list.html'}, name='people'),
    url(r'^profile/(?P<slug>[-\w]+)/past_events/$', 'profile_past_events', name='profile_past_events'),
    url(r'^password/$', 'change_password', name='change_password'),
    url(r'^password/success/$', 'view_profile', {'password_changed': True}, name='password_changed'),
)


urlpatterns += patterns('django.views.generic',
    url(r'^password/reset/sent/$', 'simple.direct_to_template', {'template': 'main/accounts/password_reset_form.html'},
                                                                            name='password_reset_sent'),
    url(r'^password/reset/done/$', 'simple.direct_to_template', {'template': 'main/accounts/password_reset_confirm.html'},
                                                                            name='password_reset_done'),
)

urlpatterns += patterns('django.contrib',
    url(r'^login/$', 'auth.views.login', {'authentication_form': LoginForm, 'template_name': 'main/index.html'},
    													name='login'),
    url(r'^logout/$', 'auth.views.logout', {'next_page': reverse_lazy('index')}, name='logout'),
    url(r'^password/reset/$', 'auth.views.password_reset', {'template_name': 'main/accounts/password_reset_form.html',
                                                        'email_template_name': 'main/accounts/password_reset_email.html',
                                                        'post_reset_redirect': reverse_lazy('password_reset_sent'),
                                                        'password_reset_form': MyPasswordResetForm},
                                                        name="forgotten"),
    url(r'^password/reset/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', 'auth.views.password_reset_confirm',
                                                        {'template_name': 'main/accounts/password_reset_confirm.html',
                                                        'post_reset_redirect': reverse_lazy('password_reset_done'),
                                                        'set_password_form': MySetPasswordForm},
                                                        name="password_reset_confirm"),
)