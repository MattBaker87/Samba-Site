from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from main.views import admin_required
from django.views.generic import list_detail

from main.forms import EventForm, EventPlayersForm
from main.models import Event, Booking

@login_required
def list_events(request, template_name, queryset_filter, paginate_by=10):
    queryset = queryset_filter(Event.objects)
    return list_detail.object_list(request, queryset=queryset,template_object_name='event',
                                    template_name=template_name, paginate_by=paginate_by)

@login_required
def detail_event(request, slug):
    target_object = get_object_or_404(Event, slug=slug)
    return render_to_response('main/events/event_detail.html', {'event': target_object},
                                                                context_instance=RequestContext(request))

@login_required
def sign_out_instrument(request, booking_id):
    target_booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST" and target_booking.user == None:
        target_booking.user = request.user
        target_booking.save()
    return HttpResponseRedirect(target_booking.event.get_absolute_url())

@login_required
def cancel_sign_out(request, booking_id):
    target_booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST" and target_booking.user == request.user:
        target_booking.user = None
        target_booking.save()
    return HttpResponseRedirect(target_booking.event.get_absolute_url())

@login_required
def coordinate_event(request, slug):
    target_event = get_object_or_404(Event, slug=slug)
    if request.method == 'POST' and target_event.coordinator == None:
        target_event.coordinator = request.user
        target_event.save()
    return HttpResponseRedirect(target_event.get_absolute_url())

@login_required
def cancel_coordinate_event(request, slug):
    target_event = get_object_or_404(Event, slug=slug)
    if request.method == 'POST' and target_event.coordinator == request.user:
        target_event.coordinator = None
        target_event.save()
    return HttpResponseRedirect(target_event.get_absolute_url())

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
