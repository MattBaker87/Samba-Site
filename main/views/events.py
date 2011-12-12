from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

from main.forms import EventForm
from main.models import Event, Booking

@login_required
def add_event(request):
    form = EventForm(data = request.POST or None)
    if form.is_valid():
        event = form.save(commit=True)
        return HttpResponseRedirect(event.get_absolute_url())

    return render_to_response('main/events/event_add.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def detail_event(request, slug):
    target_object = get_object_or_404(Event, slug=slug)
    return render_to_response('main/events/event_detail.html', {'event': target_object},
                                                                context_instance=RequestContext(request))

@login_required
def edit_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    form = EventForm(data = request.POST or None, instance = event)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(event.get_absolute_url())

    return render_to_response('main/events/event_edit.html', {'form': form, 'event': event },
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
def delete_event(request, slug):
    target_object = get_object_or_404(Event, slug=slug)
    if request.method == "POST":
        target_object.delete()
        return HttpResponseRedirect(reverse('events_upcoming'))
    else:
        return render_to_response('main/events/event_delete.html', {'event': target_object},
                                                                                    context_instance=RequestContext(request))

@login_required
def list_events(request, template_name, queryset_filter, paginate_by=None):
    event_list = queryset_filter(Event.objects)
    return render_to_response(template_name, {'event_list': event_list}, context_instance=RequestContext(request))