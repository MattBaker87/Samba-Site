from functools import wraps
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView, View
from django.utils.decorators import method_decorator

def admin_required(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponse("Sorry, you do not have admin privileges.")
        return fn(request, *args, **kwargs)
    return login_required(wrapper)

def active_required(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_active:
            return HttpResponseRedirect('index')
        return fn(request, *args, **kwargs)
    return login_required(wrapper)

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('login'))

class ActiveViewMixin(View):
    @method_decorator(active_required)
    def dispatch(self, *args, **kwargs):
        return super(ActiveViewMixin, self).dispatch(*args, **kwargs)

class AdminViewMixin(View):
    @method_decorator(admin_required)
    def dispatch(self, *args, **kwargs):
        return super(AdminViewMixin, self).dispatch(*args, **kwargs)

class AdminTemplateView(TemplateView, AdminViewMixin):
    pass

class ActiveTemplateView(TemplateView, ActiveViewMixin):
    pass