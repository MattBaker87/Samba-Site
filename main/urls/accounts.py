from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from main.views import ActiveTemplateView
from main.views.accounts import ProfilePastEvents, ListAccounts, EditProfile, ViewProfile, ChangePassword, ModerateNewUser
from django.views.generic.base import TemplateView
from registration.views import activate
from registration.views import register

from main.forms import LoginForm, MyPasswordResetForm, MySetPasswordForm, UserSignupForm

reverse_lazy = lazy(reverse, str)

######### View and edit profile (includes homepage and list of all users) ##########
urlpatterns = patterns('sambasite.main.views.accounts',
    url(r'^home/$', ActiveTemplateView.as_view(template_name='main/accounts/home.html'), name='home'),
    url(r'^profile/$', ViewProfile.as_view(), name='profile'),
    url(r'^profile/(?P<slug>[-\w]+)/$', ViewProfile.as_view(), name='view_profile'),
    url(r'^profile/(?P<slug>[-\w]+)/past_events/$', ProfilePastEvents.as_view(paginate_by=10), name='profile_past_events'),
    url(r'^edit/$', EditProfile.as_view(), name='edit_contact'),
    url(r'^list/$', ListAccounts.as_view(), name='people'),
    url(r'^password/$', ChangePassword.as_view(), name='change_password'),
    url(r'^password/success/$', ViewProfile.as_view(), {'password_changed': True}, name='password_changed'),
)

######### Password reset ##########
urlpatterns += patterns('django.contrib',
    url(r'^password/reset/$', 'auth.views.password_reset', {'template_name': 'main/not_logged_in/password_reset_request.html',
                                                        'email_template_name': 'main/not_logged_in/password_reset_email.html',
                                                        'post_reset_redirect': reverse_lazy('password_reset_sent'),
                                                        'password_reset_form': MyPasswordResetForm},
                                                        name="forgotten"),
    url(r'^password/reset/sent/$', TemplateView.as_view(template_name='main/not_logged_in/password_reset_sent.html'),
                                                                            name='password_reset_sent'),
    url(r'^password/reset/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', 'auth.views.password_reset_confirm',
                                                        {'template_name': 'main/not_logged_in/password_reset_form.html',
                                                        'post_reset_redirect': reverse_lazy('password_reset_done'),
                                                        'set_password_form': MySetPasswordForm},
                                                        name="password_reset_confirm"),
    url(r'^password/reset/done/$', TemplateView.as_view(template_name='main/not_logged_in/password_reset_success.html'),
                                                                            name='password_reset_done'),
)

########### Login and signup ############
urlpatterns += patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'authentication_form': LoginForm,
                                                        'template_name': 'main/not_logged_in/index.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': reverse_lazy('index')}, name='logout'),
    url(r'^signup/$', register, { 'backend': 'main.auth_backends.RegistrationBackend', 'form_class': UserSignupForm,
                                    'template_name': 'main/not_logged_in/signup.html',
                                    'success_url': reverse_lazy('signup_complete'),
                                    'disallowed_url': reverse_lazy('signup_disallowed')},
                                    name='signup'),                              
    url(r'^signup/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'),
                                    name='signup_disallowed'),
    url(r'^signup/complete/$', TemplateView.as_view(template_name='main/not_logged_in/signup.html'), name='signup_complete'),
                                    # Activation keys get matched by \w+ instead of the more specific
                                    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                                    # that way it can return a sensible "invalid key" message instead of a
                                    # confusing 404.
    url(r'^signup/moderate/(?P<activation_key>\w+)/$', ModerateNewUser.as_view(),
                                    { 'backend': 'main.auth_backends.RegistrationBackend',
                                    'success_url': reverse_lazy('admin_users') },
                                    name='moderate_new_users'),
)