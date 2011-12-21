from datetime import datetime

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.html import escape, linebreaks

from main.widgets import MySplitDateTimeWidget

from main import fields

from django.contrib.auth.models import User
from main.models import UserProfile, Instrument, Event, Booking, InstrumentNote

from django.db import IntegrityError

class ContactForm(forms.Form):
    """
    Update contact details
    """
    name =  forms.CharField(label=_("Name"), max_length=30,
                help_text = _("This is the name you'll be known as on the site."),
                error_messages = {'required': _("You didn't enter a display name. We need that!"),
                                    'invalid': _("Your display name should be 30 characters or fewer.")},
                widget = forms.TextInput(attrs={'placeholder':'Display name', 'label':'name'}))

    email = forms.EmailField(label=_("Email"), max_length=75,
                help_text = _("Required - we'll send you an activation email there."),
                error_messages = {'invalid': _("Please enter a valid email address. We need that to work!"),
                                    'required': _("You didn't enter an email address. We need that!")},
                widget = forms.TextInput(attrs={'placeholder':'Email', 'label':'email'}))

    telephone = fields.UKPhoneNumberField(reject=(None, 'premium', 'service'),
                help_text = _("Required. We use this to help organise, and to chase down drums."),
                error_messages = {'required': _("You didn't enter a phone number. We need that!")},
                widget = forms.TextInput(attrs={'placeholder':'Mobile phone number', 'label':'telephone'}))
    
    def __init__(self, instance=None, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.instance = instance
        if instance:
            for key in self.fields:
                self.fields[key].widget.attrs['class'] = "span3"
            self.fields['email'].initial = self.instance.email
            self.fields['name'].initial = self.instance.get_profile().name
            self.fields['telephone'].initial = self.instance.get_profile().telephone

    def clean_email(self):
        if self.instance and self.cleaned_data["email"] == self.instance.email:
            return self.cleaned_data["email"]
        try:
            User.objects.get(email=self.cleaned_data["email"])
        except User.DoesNotExist:
            return self.cleaned_data["email"]
        raise forms.ValidationError(_("A user with that email address already exists."))

    def clean_name(self):
        if self.instance and slugify(self.cleaned_data["name"]) == slugify(self.instance.get_profile().name):
            return self.cleaned_data["name"]
        try:
            User.objects.get(username=slugify(self.cleaned_data["name"]))
        except User.DoesNotExist:
            return self.cleaned_data["name"]
        raise forms.ValidationError(_("A user with that display name already exists."))

    def save(self, commit=True):
        if not self.instance:
            return None
        user = self.instance
        user.email = self.cleaned_data["email"]
        user.username = slugify(self.cleaned_data["name"])
        profile = self.instance.get_profile()
        profile.name = self.cleaned_data["name"]
        profile.telephone = self.cleaned_data["telephone"]
        if commit:
            user.save()
            profile.save()
        return user


class UserSignupForm(ContactForm):
    """
    Used for user registration. Requires users to give it a display name, email, telephone and password.
    Creates a username from the display name by slugifying it.
    """
    password1 = forms.CharField(label=_("Password"),
                widget=forms.PasswordInput(attrs={'placeholder':'Password', 'label':'password'}, render_value=False),
                error_messages = {'required': _("You didn't enter a password. You need a password!")})
    
    password2 = forms.CharField(label=_("Password (again)"),
                widget=forms.PasswordInput(attrs={'placeholder':'Password (check)', 'label':'password_again'}, render_value=False),
                error_messages = {'required': _("You didn't confirm your password. There could be typos.")},
                help_text = _("Enter the same password as above, for verification."))
    
    def __init__(self, *args, **kwargs):
        """
        Just used to reorder fields
        """
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['name', 'password1', 'password2', 'email', 'telephone']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
    
    def clean(self):
        """
        Slugify name and store it in the cleaned data as username
        """
        if 'name' in self.cleaned_data:
            self.cleaned_data["username"] = slugify(self.cleaned_data["name"])
        return self.cleaned_data


class LoginForm(AuthenticationForm):
    """
    Adds placeholders to AuthenticationForm and adjust error text.
    All errors are given in form.errors, rather than being field specific.
    """
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder':'Email', 'label':'email'})
        self.fields['password'].widget.attrs.update({'placeholder':'Password', 'label':'password'})
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                if User.objects.filter(username=username).exists() or User.objects.filter(email=username).exists():
                    raise forms.ValidationError(_("Password didn't match username/email"))
                else:
                    raise forms.ValidationError(_("No account with that username/email"))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive"))
        self.check_for_test_cookie()
        return self.cleaned_data


class InstrumentForm(forms.ModelForm):
    """
    Used to add and edit instruments. Checks if new/edited instrument slug will be a duplicate.
    """
    class Meta:
        model = Instrument
        widgets = {'name': forms.TextInput(attrs={'placeholder':'Agogo 1 (example)'}),}
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        if slugify(name) == slugify(self.instance.name):
            return name
        try:
            instrument = Instrument.objects.get(slug=slugify(name))
        except Instrument.DoesNotExist:
            return name
        raise forms.ValidationError(_("%s already exists" % instrument.get_linked_name()))


class EventForm(forms.ModelForm):
    """
    Edit and create event details (not players).
    """
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['start'].help_text = _("Use dd/mm/yyyy, hh:mm format")
        self.fields['coordinator'] = fields.OrganiserChoiceField(required=False, initial=self.instance.coordinator,
                                                        queryset=User.objects.filter(is_active=True).order_by('userprofile'))
        for instrument in Instrument.live.all():
            self.fields[instrument.name] = forms.BooleanField(required=False,
                    label=mark_safe(instrument.name +
                        ' <span class="label important">Dmg</span>' if instrument.damaged else instrument.name ),
                    initial= self.instance.bookings.filter(instrument=instrument).exists())
    
    class Meta:
        model = Event
        widgets = {
                    'name': forms.TextInput(attrs={'placeholder':'e.g., UNISON and UNITE Strike Day', 'class':'span7'}),
                    'start': MySplitDateTimeWidget(attrs={'class':'datetimefield'}, date_placeholder="31/12/2011",
                                                                                    time_placeholder="12:00"),
                    'notes': forms.Textarea(attrs={'class':'span7', 'rows':'4'}),
                    }
    
    
    def instrument_fields(self):
        return [self[instrument.name] for instrument in Instrument.live.all()]
    
    # TODO: Make this less of a hack...
    def non_instrument_fields(self):
        return [field for field in self if not field.name in [i.name for i in self.instrument_fields()]]
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        if slugify(name) == slugify(self.instance.name):
            return name
        try:
            Event.objects.get(slug=slugify(name))
        except Event.DoesNotExist:
            return name
        raise forms.ValidationError(_("An event with that name already exists"))
    
    def clean_start(self):
        start = self.cleaned_data["start"]
        if start <= datetime.now():
            raise forms.ValidationError(_("Please enter a date in the future"))
        return start
    
    def save(self, commit=True):
        event = super(EventForm, self).save(commit=False)
        if commit:
            event.save()
            for field in self.instrument_fields():
                if self.cleaned_data[field.name]:
                    Booking.objects.get_or_create(instrument=Instrument.live.get(name=field.name), event=event)
                else:
                    Booking.objects.filter(instrument=Instrument.live.get(name=field.name), event=event).delete()
        return event

class EventPlayersForm(forms.Form):
    """
    Edit players at a given event.
    """
    def __init__(self, instance=None, *args, **kwargs):
        super(EventPlayersForm, self).__init__(*args, **kwargs)
        self.event = instance
        for b in self.event.bookings.all():
            self.fields[b.instrument.name] = forms.ModelChoiceField(label=mark_safe(b.instrument.name),
                                                queryset=UserProfile.objects.filter(user__is_active=True),
                                                required=False, initial=b.user.get_profile() if b.user else None,)
    
    def save(self, commit=True):
        if commit:
            for field in self.fields:
                b = self.event.bookings.get(instrument=Instrument.live.get(name=field))
                b.user = self.cleaned_data[field].user if self.cleaned_data[field] else None
                b.save()
        return self.event


class InstrumentNoteForm(forms.ModelForm):
    """
    Write an (optional) note on an instrument
    """
    def __init__(self, event=None, instrument=None, user=None, *args, **kwargs):
        super(InstrumentNoteForm, self).__init__(*args, **kwargs)
        self.event = event
        self.instrument = instrument
        self.user = user
    
    class Meta:
        model = InstrumentNote
        fields = ['note']
        widgets = {'note': forms.Textarea(attrs={'class':'span9', 'rows':'3'})}
    
    def save(self, commit=True):
        note = super(InstrumentNoteForm, self).save(commit=False)
        note.event = self.event
        note.instrument = self.instrument
        note.user = self.user
        note.date_made = datetime.now()
        note.subject = "general"
        if commit and note.note:
            note.save()
        return note


class InstrumentNoteRequiredForm(InstrumentNoteForm):
    """
    Subclass of InstrumentNoteForm that makes the note required
    """
    def __init__(self, *args, **kwargs):
        super(InstrumentNoteRequiredForm, self).__init__(*args, **kwargs)
        self.fields['note'].required = True
        self.fields['note'].error_messages = {'required': _("Please enter a note.")}


class AdminBookingSigninForm(forms.Form):
    """
    Booking signin form used by admins (has drop-down selection of the booking they're signing in).
    """
    def __init__(self, instrument=None, admin=None, *args, **kwargs):
        super(AdminBookingSigninForm, self).__init__(*args, **kwargs)
        self.instrument = instrument
        self.admin = admin
        self.fields['damaged'] = InstrumentForm(instance=self.instrument).fields['damaged']
        self.fields['damaged'].initial = instrument.damaged
        self.fields['booking'] = fields.BookingChoiceField(label=mark_safe("Last booking instrument was returned after"),
                                                            queryset=self.instrument.bookings.not_signed_in(),
                                                            empty_label=None, initial=instrument.get_last_booking(),)
    
    note = InstrumentNoteForm().fields['note']
    note.required = False
    
    def get_booking(self):
        return self.cleaned_data['booking']
    
    def write_note(self):
        booking = self.get_booking()
        InstrumentNote.objects.create(instrument=booking.instrument, user=booking.user, event=booking.event,
                                date_made=booking.event.start, subject="event")
        if self.cleaned_data['note']:
            InstrumentNote.objects.create(instrument=booking.instrument, user=self.admin,
                                    date_made=datetime.now(), note=self.cleaned_data['note'], subject="general")
        if self.has_changed() and 'damaged' in self._changed_data:
            InstrumentNote.objects.create(instrument=booking.instrument, user=self.admin,
                                    date_made=datetime.now(), subject="damage" if self.cleaned_data['damaged'] else "repair")
    
    def save(self, commit=True):
        booking = self.get_booking()
        if commit:
            booking.signed_in = True
            booking.save()
            booking.instrument.damaged = self.cleaned_data['damaged']
            booking.instrument.save()
            self.write_note()
            for b in booking.instrument.bookings.not_signed_in().filter(event__start__lt=booking.event.start):
                b.signed_in = True
                b.save()
                note = InstrumentNote(instrument=b.instrument, user=b.user, event=b.event, date_made=b.event.start, subject="event")
                note.save()
        return booking.instrument


class BookingSigninForm(AdminBookingSigninForm):
    """
    User sign-in form is the same as the admin one, but they don't set the booking and they write different notes.
    """
    def __init__(self, booking=None, *args, **kwargs):
        super(BookingSigninForm, self).__init__(instrument=booking.instrument, *args, **kwargs)
        self.fields.pop('booking')
        self.booking = booking
    
    def get_booking(self):
        return self.booking
    
    def write_note(self):
        booking = self.get_booking()
        InstrumentNote.objects.create(instrument=booking.instrument, user=booking.user, event=booking.event,
                                date_made=booking.event.start, note=self.cleaned_data['note'], subject="event")
        if self.has_changed() and 'damaged' in self._changed_data:
            InstrumentNote.objects.create(instrument=booking.instrument, user=booking.user, date_made=datetime.now(),
                                subject="damage" if self.cleaned_data['damaged'] else "repair")


class MyPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput(attrs={'class':'span3'}))
    new_password2 = forms.CharField(label=_("New password (again)"), widget=forms.PasswordInput(attrs={'class':'span3'}))
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput(attrs={'class':'span3'}))


class MyPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(MyPasswordResetForm, self).__init__(*args, **args)
        self.fields['email'].widget = forms.TextInput(attrs={'placeholder':'Email'})

    
class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput(attrs={'placeholder':'New password'}))
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                                widget=forms.PasswordInput(attrs={'placeholder':'New password confirmation'}))
