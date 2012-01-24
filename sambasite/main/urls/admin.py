from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from main.views.admin import AdminEvents, AdminInstruments, AdminUsers

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('sambasite.main.views.admin',
    url(r'^events/$', AdminEvents.as_view(), name='admin_events'),
    url(r'^instruments/$', AdminInstruments.as_view(), name='admin_instruments'),
    url(r'^users/$', AdminUsers.as_view(), name='admin_users'),
    url(r'^users/added/$', AdminUsers.as_view(), {'action': 'added'}, name='admin_users_success'),
    url(r'^users/denied/$', AdminUsers.as_view(), {'action': 'denied'}, name='admin_users_denied'),
)
