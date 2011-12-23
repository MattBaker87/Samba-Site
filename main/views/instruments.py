from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from django.views.generic import ListView, FormView, CreateView, UpdateView
from main.views import ActiveViewMixin, AdminViewMixin, FormMixin, ChangeObjectView

from main.forms import InstrumentForm, BookingSigninForm, AdminBookingSigninForm, InstrumentNoteForm, InstrumentNoteRequiredForm
from main.models import Instrument, Booking, InstrumentNote

from datetime import datetime
from copy import copy

reverse_lazy = lazy(reverse, str)

class ListInstruments(ListView, ActiveViewMixin):
    paginate_by=None


class AddInstrument(CreateView, AdminViewMixin):
    form_class = InstrumentForm
    template_name = 'main/instruments/instrument_add.html'
    success_url = reverse_lazy('instrument_list')

    def form_valid(self, form):
        self.object = form.save(commit=True)
        InstrumentNote.objects.create(instrument=self.object, user=self.request.user, date_made=datetime.now(), subject="added")
        return HttpResponseRedirect(self.get_success_url())


class EditInstrument(UpdateView, AdminViewMixin):
    form_class = InstrumentForm
    model = Instrument
    template_name = 'main/instruments/instrument_edit.html'

    def form_valid(self, form):
        self.old_obj = copy(self.get_object())
        self.object = form.save(commit=True)
        if form.has_changed():
            if 'damaged' in form._changed_data:
                InstrumentNote.objects.create(instrument=self.object, user=self.request.user, date_made=datetime.now(),
                            subject="damage" if self.object.damaged else "repair")
            if 'name' in form._changed_data:
                InstrumentNote.objects.create(instrument=self.object, user=self.request.user, date_made=datetime.now(),
                            subject="rename", note="from '%s' to '%s'" % (self.old_obj.name, self.object.name))
            if 'instrument_type' in form._changed_data:
                InstrumentNote.objects.create(instrument=self.object, user=self.request.user, date_made=datetime.now(),
                            subject="type", note="from %s to %s" % (self.old_obj.get_instrument_type_display(),
                                                                    self.object.get_instrument_type_display()))
        return HttpResponseRedirect(self.get_success_url())


class RemoveNote(ChangeObjectView, ActiveViewMixin):
    model = InstrumentNote
    
    def change_object(self, obj):
        if obj.is_editable and (self.request.user.is_staff or self.request.user == obj.user):
            obj.is_removed = True
            obj.save()

    def get_success_url(self):
        return self.object.instrument.get_absolute_url()
    

########## All views below here need to display an instrument's notes, so subclass ListView #############
class DetailInstrument(ListView, ActiveViewMixin):    
    template_name='main/instruments/instrument_detail.html'
    paginate_by=10
    context_object_name='notes_list'

    def dispatch(self, request, *args, **kwargs):
        self.instrument = get_object_or_404(Instrument, slug=kwargs.pop('slug'))
        return super(DetailInstrument, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.instrument.user_notes.filter(is_removed=False)

    def get_context_data(self, **kwargs):
        context = super(DetailInstrument, self).get_context_data(**kwargs)
        context['instrument'] = self.instrument
        return context


class InstrumentWriteNote(DetailInstrument, FormMixin):
    """
    Provides the basis for other views that need to have a form and return all of the instrument's notes.
    """
    form_class = InstrumentNoteForm
    form_context_name = 'new_note_form'
    
    def get(self, request, *args, **kwargs):
        form_class = self.form_class
        self.form = self.form_class(**self.get_form_kwargs())
        return super(InstrumentWriteNote, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.form_class
        self.form = self.form_class(**self.get_form_kwargs())
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)
    
    def get_additional_form_args(self):
        return {'instrument': self.instrument, 'user': self.request.user}
    
    def form_valid(self, form):
        note = form.save(commit=False)
        note.is_editable = True
        note.subject = "general"
        if note.note:
            note.save()
        return HttpResponseRedirect(self.instrument.get_absolute_url())
    
    def form_invalid(self, form):
        return super(InstrumentWriteNote, self).get(self.request, *self.args, **self.kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(InstrumentWriteNote, self).get_context_data(**kwargs)
        context[self.form_context_name] = self.form
        return context


class DeleteInstrument(InstrumentWriteNote, AdminViewMixin):
    form_class = InstrumentNoteRequiredForm
    form_context_name = 'form'
    template_name = 'main/instruments/instrument_delete.html'
    
    def form_valid(self, form):
        self.instrument.do_remove()
        note = form.save(commit=False)
        note.subject = "remove"
        note.save()
        return HttpResponseRedirect(reverse_lazy('instrument_list'))


class ResurrectInstrument(InstrumentWriteNote, AdminViewMixin):
    form_class = InstrumentNoteRequiredForm
    form_context_name = 'form'
    template_name = 'main/instruments/instrument_resurrect.html'

    def form_valid(self, form):
        self.instrument.is_removed = False
        self.instrument.save()
        note = form.save(commit=False)
        note.subject = "resurrect"
        note.save()
        return HttpResponseRedirect(self.instrument.get_absolute_url())


class SignInInstrument(InstrumentWriteNote, AdminViewMixin):
    form_class = AdminBookingSigninForm
    form_context_name = 'form'
    template_name = 'main/instruments/instrument_signin_admin.html'
    
    def dispatch(self, request, *args, **kwargs):
        instrument = get_object_or_404(Instrument.live.all(), slug=kwargs['slug'])
        if instrument.get_signed_in():
            return HttpResponseRedirect(instrument.get_absolute_url())
        return super(SignInInstrument, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.instrument.get_absolute_url())


class SignInBooking(InstrumentWriteNote):
    template_name='main/instruments/instrument_signin.html'
    form_class = BookingSigninForm
    form_context_name = 'form'

    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(Booking, id=kwargs.pop('booking_id'))
        if not self.booking.user == request.user or self.booking.signed_in:
            return HttpResponseRedirect(self.booking.instrument.get_absolute_url())
        return super(SignInBooking, self).dispatch(request, *args, slug=self.booking.instrument.slug, **kwargs)
    
    def get_additional_form_args(self):
        return {'booking': self.booking}
    
    def get_context_data(self, **kwargs):
        context = super(SignInBooking, self).get_context_data(**kwargs)
        context['booking'] = self.booking
        return context

    def form_valid(self, form):
        self.form.save()
        return HttpResponseRedirect(self.booking.instrument.get_absolute_url())
