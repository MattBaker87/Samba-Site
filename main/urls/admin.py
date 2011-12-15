from django.conf.urls.defaults import include, patterns, url
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('sambasite.main.views.admin',
    url(r'^home/$', 'admin_home', name='admin_home'),
)
