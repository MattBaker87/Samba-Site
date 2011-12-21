from django.views.generic import ListView
from main.views import AdminViewMixin

from main.models import Event

class AdminHome(ListView, AdminViewMixin):
    def get_queryset(self):
        return Event.objects.future_events()
    
    template_name = 'main/admin_home.html'
    paginate_by = 5