from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

from main.forms import InstrumentForm
from main.models import Instrument

@login_required
def add_instrument(request):
    if request.method == "POST":
        form = InstrumentForm(data = request.POST)
        if form.is_valid():
            instrument = form.save(commit=True)
            return HttpResponseRedirect(reverse('instrument_list'))
    else:
        form = InstrumentForm()
    return render_to_response('main/instruments/instrument_add.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def delete_instrument(request, slug):
    target_object = get_object_or_404(Instrument, slug=slug)
    if request.method == "POST":
        target_object.delete()
        return HttpResponseRedirect(reverse('instrument_list'))
    else:
        return render_to_response('main/instruments/instrument_delete.html', {'instrument': target_object}, context_instance=RequestContext(request))

@login_required
def detail_instrument(request, slug):
    target_object = get_object_or_404(Instrument, slug=slug)
    return render_to_response('main/instruments/instrument_detail.html', {'instrument': target_object},
                                                                context_instance=RequestContext(request))