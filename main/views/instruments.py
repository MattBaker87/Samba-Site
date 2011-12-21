from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from main.views import admin_required, active_required

from django.views.generic import list_detail
from django.views.generic import ListView
from main.views import ActiveViewMixin

from main.forms import InstrumentForm, BookingSigninForm, AdminBookingSigninForm, InstrumentNoteForm, InstrumentNoteRequiredForm
from main.models import Instrument, Booking, InstrumentNote

from datetime import datetime

class ListInstruments(ListView, ActiveViewMixin):
    paginate_by=None
    

class DetailInstrument(ListInstruments):
    def get_queryset(self):
        self.target_instrument = get_object_or_404(Instrument, slug=self.kwargs['slug'])
        return self.target_instrument.user_notes.filter(is_removed=False)
    
    def get_context_data(self, **kwargs):
        context = super(DetailInstrument, self).get_context_data(**kwargs)
        context['instrument'] = self.target_instrument
        return context
    
    template_name='main/instruments/instrument_detail.html'
    paginate_by=10
    context_object_name = 'notes_list'


@active_required
def detail_instrument(request, slug, paginate_by=10, extra_context=None, template_name='main/instruments/instrument_detail.html'):
    target_object = get_object_or_404(Instrument, slug=slug)
    c = {'instrument': target_object}
    if extra_context:
        c.update(extra_context)
    return list_detail.object_list(request, template_name=template_name, template_object_name='notes', paginate_by=paginate_by,
                                queryset=target_object.user_notes.filter(is_removed=False), extra_context=c)

@active_required
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

@active_required
def instrument_write_note(request, slug):
    target_object = get_object_or_404(Instrument, slug=slug)
    form = InstrumentNoteForm(data = request.POST or None, instrument=target_object, user=request.user)
    if form.is_valid():
        note = form.save(commit=False)
        note.is_editable = True
        note.subject = "general"
        note.save()
        return HttpResponseRedirect(target_object.get_absolute_url())
    return detail_instrument(request, slug=target_object.slug, extra_context={'new_note_form': form})

@active_required
def remove_note(request, note_id):
    target_object = get_object_or_404(InstrumentNote, id=note_id)
    if request.method == "POST" and (request.user.is_staff or request.user == target_object.user):
        target_object.is_removed = True
        target_object.save()
    return HttpResponseRedirect(target_object.instrument.get_absolute_url())

@admin_required
def add_instrument(request):
    form = InstrumentForm(data = request.POST or None)
    if form.is_valid():
        instrument = form.save(commit=True)
        InstrumentNote.objects.create(instrument=instrument, user=request.user, date_made=datetime.now(), subject="added")
        return HttpResponseRedirect(reverse('instrument_list'))
    return render_to_response('main/instruments/instrument_add.html', {'form': form}, context_instance=RequestContext(request))

@admin_required
def edit_instrument(request, slug):
    instrument = get_object_or_404(Instrument.live.all(), slug=slug)
    i_old_name = str(instrument.name)
    i_old_type = str(instrument.get_instrument_type_display())
    form = InstrumentForm(data = request.POST or None, instance = instrument)
    if form.is_valid():
        new_instrument = form.save(commit=True)
        if form.has_changed():
            if 'damaged' in form._changed_data:
                InstrumentNote.objects.create(instrument=instrument, user=request.user, date_made=datetime.now(),
                                            subject="damage" if instrument.damaged else "repair")
            if 'name' in form._changed_data:
                InstrumentNote.objects.create(instrument=instrument, user=request.user, date_made=datetime.now(),
                                            subject="rename", note="from %s to %s" % (i_old_name, instrument.name))
            if 'instrument_type' in form._changed_data:
                InstrumentNote.objects.create(instrument=instrument, user=request.user, date_made=datetime.now(), subject="type",
                                            note="from %s to %s" % (i_old_type, instrument.get_instrument_type_display()))
        return HttpResponseRedirect(instrument.get_absolute_url())
    return render_to_response('main/instruments/instrument_edit.html', {'form': form, 'instrument': instrument },
                                                                                    context_instance=RequestContext(request))

@admin_required
def delete_instrument(request, slug):
    target_object = get_object_or_404(Instrument.live.all(), slug=slug)
    form = InstrumentNoteRequiredForm(data = request.POST or None, instrument=target_object, user=request.user)
    if form.is_valid():
        target_object.do_remove()
        note = form.save(commit=False)
        note.subject = "remove"
        note.save()
        return HttpResponseRedirect(reverse('instrument_list'))
    else:
        return detail_instrument(request, slug=target_object.slug, extra_context={'form':form},
                                                                template_name='main/instruments/instrument_delete.html')

@admin_required
def resurrect_instrument(request, slug):
    target_object = get_object_or_404(Instrument.objects.filter(is_removed=True), slug=slug)
    form = InstrumentNoteRequiredForm(data = request.POST or None, instrument=target_object, user=request.user)
    if form.is_valid():
        target_object.is_removed = False
        target_object.save()
        note = form.save(commit=False)
        note.subject = "resurrect"
        note.save()
        return HttpResponseRedirect(target_object.get_absolute_url())
    else:
        return detail_instrument(request, slug=target_object.slug, extra_context={'form':form},
                                                                template_name='main/instruments/instrument_resurrect.html')

@admin_required
def sign_in_instrument(request, slug):
    target_instrument = get_object_or_404(Instrument.live.all(), slug=slug)
    if target_instrument.get_signed_in():
        return HttpResponseRedirect(target_instrument.get_absolute_url())
    form = AdminBookingSigninForm(data = request.POST or None, instrument = target_instrument, admin=request.user)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(target_instrument.get_absolute_url())
    return detail_instrument(request, slug=target_instrument.slug, template_name='main/instruments/instrument_signin_admin.html',
                                extra_context={'form': form})