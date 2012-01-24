from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from main.views import ActiveViewMixin, AdminViewMixin, ChangeObjectView

from main.forms import EventForm, EventPlayersForm
from main.models import Event, Booking

reverse_lazy = lazy(reverse, str)

# All views here are class based. All use generic views as subclasses, except
# the ChangeObjectView based ones - the base view for this is in __init__ and
# it's used to change an object using POST but without using a form

class ListEvents(ListView, ActiveViewMixin):
    paginate_by = 10


class DetailEvent(DetailView, ActiveViewMixin):
    model = Event
    template_name = 'main/events/event_detail.html'


class BookInstrument(ChangeObjectView, ActiveViewMixin):
    model = Booking
    
    def change_object(self, obj):
        if obj.user == None:
            obj.user = self.request.user
            obj.save()
        elif obj.user == self.request.user:
            obj.user = None
            obj.save()


class CoordinateEvent(ChangeObjectView, ActiveViewMixin):
    model = Event
    
    def change_object(self, obj):
        if obj.coordinator == None:
            obj.coordinator = self.request.user
            obj.save()
        elif obj.coordinator == self.request.user:
            obj.coordinator = None
            obj.save()


class AddEvent(CreateView, AdminViewMixin):
    form_class = EventForm
    template_name = 'main/events/event_add.html'


class EditEvent(UpdateView, AdminViewMixin):
    form_class = EventForm
    model = Event
    template_name = 'main/events/event_edit.html'


class DeleteEvent(DeleteView, AdminViewMixin):
    model = Event
    success_url = reverse_lazy('events_upcoming')
    template_name = 'main/events/event_delete.html'


class EditEventPlayers(UpdateView, AdminViewMixin):
    form_class = EventPlayersForm
    model = Event
    template_name = 'main/events/event_edit_players.html'
