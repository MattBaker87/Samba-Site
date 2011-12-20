from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from main.forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm, UserSignupFormNew

from datetime import datetime, timedelta

reverse_lazy = lazy(reverse, str)

##### Used by django-registration URLs #####
from django.views.generic.simple import direct_to_template

from registration.views import activate
from registration.views import register

urlpatterns = patterns('sambasite.main.views.accounts',
    url(r'^edit/$', 'edit_profile', name='edit_contact'),
    url(r'^profile/$', 'view_profile', name='profile'),
    url(r'^profile/(?P<slug>[-\w]+)/$', 'view_profile', name='view_profile'),
    url(r'^list/$', 'list_accounts', {'queryset_filter':lambda x:x.filter(last_login__gte=datetime.now()-timedelta(365), is_active=True).order_by('userprofile__name'),
                                        'template_name': 'main/accounts/accounts_list.html'}, name='people'),
    url(r'^profile/(?P<slug>[-\w]+)/past_events/$', 'profile_past_events', {'paginate_by': 10}, name='profile_past_events'),
    url(r'^password/$', 'change_password', name='change_password'),
    url(r'^password/success/$', 'view_profile', {'password_changed': True}, name='password_changed'),
)


urlpatterns += patterns('django.views.generic',
    url(r'^password/reset/sent/$', 'simple.direct_to_template', {'template': 'main/accounts/password_reset_form.html'},
                                                                            name='password_reset_sent'),
    url(r'^password/reset/done/$', 'simple.direct_to_template', {'template': 'main/accounts/password_reset_confirm.html'},
                                                                            name='password_reset_done'),
    url(r'^home/$', 'simple.direct_to_template', {'template': 'main/home.html'}, name='home')
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

########### Patterns for user registration (uses django-registration) ############
urlpatterns += patterns('',
    url(r'^signup/$', register, { 'backend': 'main.auth_backends.RegistrationBackend', 'form_class': UserSignupFormNew,
                                    'template_name': 'main/accounts/signup.html', 'success_url': reverse_lazy('signup_complete'),
                                    'disallowed_url': reverse_lazy('signup_disallowed')},
                                    name='signup'),                              
    url(r'^signup/closed/$', direct_to_template, { 'template': 'registration/registration_closed.html' },
                                    name='signup_disallowed'),
    url(r'^signup/complete/$', direct_to_template, { 'template': 'main/accounts/signup.html' }, name='signup_complete'),
                                    # Activation keys get matched by \w+ instead of the more specific
                                    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                                    # that way it can return a sensible "invalid key" message instead of a
                                    # confusing 404.
    url(r'^signup/moderate/(?P<activation_key>\w+)/$', 'sambasite.main.views.accounts.moderate_new_users',
                                    { 'backend': 'main.auth_backends.RegistrationBackend',
                                    'success_url': reverse_lazy('admin_home') },
                                    name='moderate_new_users'),
)