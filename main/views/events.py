from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from main.views import admin_required, active_required

from django.views.generic import ListView, DetailView
from main.views import ActiveViewMixin, ChangeObjectView

from main.forms import EventForm, EventPlayersForm
from main.models import Event, Booking


class ListEvents(ListView, ActiveViewMixin):
    paginate_by = 10

class DetailEvent(DetailView, ActiveViewMixin):
    model = Event
    template_name = 'main/events/event_detail.html'

class BookInstrument(ChangeObjectView, ActiveViewMixin):
    def get_object(self, **kwargs):
        return get_object_or_404(Booking, id=kwargs['booking_id'])
    
    def change_object(self, obj):
        if obj.user == None:
            obj.user = self.request.user
            obj.save()
        elif obj.user == self.request.user:
            obj.user = None
            obj.save()
    
    def get_redirect(self):
        return self.target_object.event.get_absolute_url()


class CoordinateEvent(ChangeObjectView, ActiveViewMixin):
    def get_object(self, **kwargs):
        return get_object_or_404(Event, slug=kwargs['slug'])

    def get_redirect(self):
        return self.target_object.get_absolute_url()

    def change_object(self, obj):
        if obj.coordinator == None:
            obj.coordinator = self.request.user
            obj.save()
        elif obj.coordinator == self.request.user:
            obj.coordinator = None
            obj.save()


@admin_required
def add_event(request):
    form = EventForm(data = request.POST or None)
    if form.is_valid():
        event = form.save(commit=True)
        return HttpResponseRedirect(event.get_absolute_url())
    return render_to_response('main/events/event_add.html', {'form': form}, context_instance=RequestContext(request))

@admin_required
def edit_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    form = EventForm(data = request.POST or None, instance = event)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(event.get_absolute_url())
    return render_to_response('main/events/event_edit.html', {'form': form, 'event': event },
                                                                                    context_instance=RequestContext(request))

@admin_required
def delete_event(request, slug):
    target_object = get_object_or_404(Event, slug=slug)
    if request.method == "POST":
        target_object.delete()
        return HttpResponseRedirect(reverse('events_upcoming'))
    else:
        return render_to_response('main/events/event_delete.html', {'event': target_object},
                                                                                    context_instance=RequestContext(request))

@admin_required
def edit_event_players(request, slug):
    event = get_object_or_404(Event, slug=slug)
    form = EventPlayersForm(data = request.POST or None, event = event)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(event.get_absolute_url())
    return render_to_response('main/events/event_edit_players.html', {'form': form, 'event': event },
                                                                                    context_instance=RequestContext(request))
