from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

from main.forms import InstrumentForm
from main.models import Instrument, Booking

@login_required
def add_instrument(request):
    form = InstrumentForm(data = request.POST or None)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(reverse('instrument_list'))

    return render_to_response('main/instruments/instrument_add.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def edit_instrument(request, slug):
    instrument = get_object_or_404(Instrument, slug=slug)
    form = InstrumentForm(data = request.POST or None, instance = instrument)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(instrument.get_absolute_url())

    return render_to_response('main/instruments/instrument_edit.html', {'form': form, 'instrument': instrument },
                                                                                    context_instance=RequestContext(request))

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

@login_required
def sign_in_instrument(request, booking_id):
    target_booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST" and target_booking.user == request.user:
        target_booking.signed_in = True
        target_booking.save()
        return HttpResponseRedirect(target_booking.instrument.get_absolute_url())
    return render_to_response('main/instruments/instrument_signin.html', {'instrument': target_booking.instrument},
                                                                context_instance=RequestContext(request))