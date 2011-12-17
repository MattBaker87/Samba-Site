from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from main.views import admin_required
from django.views.generic import list_detail

from main.forms import InstrumentForm, BookingSigninForm, AdminBookingSigninForm, InstrumentNoteForm
from main.models import Instrument, Booking, InstrumentNote

@login_required
def detail_instrument(request, slug, paginate_by=10, extra_context=None, template_name='main/instruments/instrument_detail.html'):
    target_object = get_object_or_404(Instrument, slug=slug)
    c = {'instrument': target_object}
    if extra_context:
        c.update(extra_context)
    return list_detail.object_list(request, template_name=template_name, template_object_name='notes', paginate_by=paginate_by,
                                queryset=target_object.user_notes.all(), extra_context=c)

@login_required
def sign_in_booking(request, booking_id):
    target_booking = get_object_or_404(Booking, id=booking_id)
    if not target_booking.user == request.user or target_booking.signed_in:
        return HttpResponseRedirect(target_booking.instrument.get_absolute_url())
    form = BookingSigninForm(data = request.POST or None, booking = target_booking)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(target_booking.instrument.get_absolute_url())
    return detail_instrument(request, slug=target_booking.instrument.slug,
                                    template_name='main/instruments/instrument_signin.html',
                                    extra_context={'booking': target_booking, 'form': form})

@login_required
def instrument_write_note(request, slug):
    target_object = get_object_or_404(Instrument, slug=slug)
    form = InstrumentNoteForm(data = request.POST or None, instrument=target_object, user=request.user)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(target_object.get_absolute_url())
    return detail_instrument(request, slug=target_object.slug, extra_context={'new_note_form': form})

@login_required
def delete_note(request, note_id):
    target_object = get_object_or_404(InstrumentNote, id=note_id)
    if request.method == "POST":
        if target_object.event:
            target_object.note = ""
            target_object.save()
        else:
            target_object.delete()
    return HttpResponseRedirect(target_object.instrument.get_absolute_url())

@admin_required
def add_instrument(request):
    form = InstrumentForm(data = request.POST or None)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(reverse('instrument_list'))
    return render_to_response('main/instruments/instrument_add.html', {'form': form}, context_instance=RequestContext(request))

@admin_required
def edit_instrument(request, slug):
    instrument = get_object_or_404(Instrument, slug=slug)
    form = InstrumentForm(data = request.POST or None, instance = instrument)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(instrument.get_absolute_url())
    return render_to_response('main/instruments/instrument_edit.html', {'form': form, 'instrument': instrument },
                                                                                    context_instance=RequestContext(request))

@admin_required
def delete_instrument(request, slug):
    target_object = get_object_or_404(Instrument, slug=slug)
    if request.method == "POST":
        target_object.delete()
        return HttpResponseRedirect(reverse('instrument_list'))
    else:
        return detail_instrument(request, slug=target_object.slug, template_name='main/instruments/instrument_delete.html')

@admin_required
def sign_in_instrument(request, slug):
    target_instrument = get_object_or_404(Instrument, slug=slug)
    if target_instrument.get_signed_in():
        return HttpResponseRedirect(target_instrument.get_absolute_url())
    form = AdminBookingSigninForm(data = request.POST or None, instrument = target_instrument, admin=request.user)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(target_instrument.get_absolute_url())
    return detail_instrument(request, slug=target_instrument.slug, template_name='main/instruments/instrument_signin_admin.html',
                                extra_context={'form': form})