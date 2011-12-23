from django.views.generic import ListView
from main.views import AdminViewMixin

from main.models import Event, Instrument
from registration.models import RegistrationProfile

class AdminEvents(ListView, AdminViewMixin):
    template_name = 'main/admin/admin_events.html'
    paginate_by = 5

    def get_queryset(self):
        return Event.objects.future_events()


class AdminInstruments(ListView, AdminViewMixin):
    template_name = 'main/admin/admin_instruments.html'
    paginate_by = 5

    def get_queryset(self):
        return Instrument.live.all()


class AdminUsers(ListView, AdminViewMixin):
    template_name = 'main/admin/admin_users.html'
    context_object_name = 'registration_list'
    paginate_by = 5

    def get_queryset(self):
        return RegistrationProfile.objects.filter(id__in=[x.id for x in RegistrationProfile.objects.all() \
                                                            if not x.activation_key_expired()]).order_by('user')
    
    def get_context_data(self, **kwargs):
        context = super(AdminUsers, self).get_context_data(**kwargs)
        context['action'] = self.kwargs['action'] if self.kwargs.has_key('action') else None
        return context