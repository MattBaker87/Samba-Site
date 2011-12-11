from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

from main.forms import EventForm
from main.models import Event

@login_required
def add_event(request):
    if request.method == "POST":
        form = EventForm(data = request.POST)
        if form.is_valid():
            event = form.save(commit=True)
            return HttpResponseRedirect(event.get_absolute_url())
    else:
        form = EventForm()
    return render_to_response('main/events/event_add.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def detail_event(request, slug):
    target_object = get_object_or_404(Event, slug=slug)
    return render_to_response('main/events/event_detail.html', {'event': target_object},
                                                                context_instance=RequestContext(request))