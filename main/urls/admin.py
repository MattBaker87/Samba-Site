from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from main.views.admin import AdminHome

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('sambasite.main.views.admin',
    url(r'^home/$', AdminHome.as_view(), name='admin_home'),
)
