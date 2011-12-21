from functools import wraps
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import SingleObjectMixin
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

class ChangeObjectView(TemplateView, SingleObjectMixin):
    """
    View that takes a single object and changes that object if the request type is POST.
    Otherwise redirects to a supplied address.
    """
    success_url = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.change_object(self.object)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        if self.success_url:
            url = self.success_url % self.object.__dict__
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def change_object(self, obj):
        pass
    