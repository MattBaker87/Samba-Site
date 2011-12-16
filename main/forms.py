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

class UserSignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder':'Password', 'label':'password'})
        self.fields['password1'].error_messages = {'required': _("You didn't enter a password. You need a password!")}
        
        self.fields['password2'].widget.attrs.update({'placeholder':'Password (check)', 'label':'password_again'})
        self.fields['password2'].help_text = _("Enter the same password as above, for verification.")
        self.fields['password2'].error_messages = {'required': _("You didn't confirm your password. There could be typos.")}
        self.fields['username'] = forms.EmailField(label=_("Email"), max_length=30,
                help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
                error_messages = {'invalid': _("Please enter a valid email address. It should be 30 characters or fewer."),
                                    'required': _("You didn't enter an email address. We need that!")},
                widget = forms.TextInput(attrs={'placeholder':'Email', 'label':'email'}))

    name = forms.CharField(label=_("Name"), max_length=30,
        help_text = _("This is the name you'll be known as on the site."),
        error_messages = {'required': _("You didn't enter a display name. We need that!")},
        widget = forms.TextInput(attrs={'placeholder':'Display name', 'label':'name'}))
    
    telephone = fields.UKPhoneNumberField(reject=(None, 'premium', 'service'),
        help_text = _("Required. We use this to help organise, and to chase down drums."),
        error_messages = {'required': _("You didn't enter a phone number. We need that!")},
        widget = forms.TextInput(attrs={'placeholder':'Mobile phone number', 'label':'telephone'}))
    
    def clean_username(self):
        try:
            super(UserSignupForm, self).clean_username()
        except forms.ValidationError:
            raise forms.ValidationError(_("A user with that email address already exists."))
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        try:
            UserProfile.objects.get(name=name)
        except UserProfile.DoesNotExist:
            return name
        raise forms.ValidationError(_("A user with that display name address already exists."))
    
    def clean_password2(self):
        try:
            super(UserSignupForm, self).clean_password2()
        except forms.ValidationError:
            raise forms.ValidationError(_("The two passwords you entered didn't match."))
    
    def save(self, commit=True):
        user = super(UserSignupForm, self).save(commit=False) 
        user.email=self.cleaned_data["username"]
        if commit:
            user.save()
            profile = UserProfile.objects.create(user=user, name=self.cleaned_data["name"],
                                                            telephone=self.cleaned_data["telephone"])
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder':'Email', 'label':'email'})
        self.fields['password'].widget.attrs.update({'placeholder':'Password', 'label':'password'})
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                raise forms.ValidationError(_("That email address isn't registered with us"))
            
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Password didn't match username"))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive"))
        self.check_for_test_cookie()
        return self.cleaned_data


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        widgets = {'name': forms.TextInput(attrs={'placeholder':'Agogo 1 (example)'}),}
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        if name == self.instance.name:
            return name
        try:
            Instrument.objects.get(slug=slugify(name))
        except Instrument.DoesNotExist:
            return name
        raise forms.ValidationError(_("Instrument already exists"))


class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['start'].help_text = _("Use dd/mm/yyyy, hh:mm format")
        for instrument in Instrument.objects.all():
            self.fields[instrument.name] = forms.BooleanField(
                    label=mark_safe(instrument.name +
                        ' <span class="label important">Damaged</span>' if instrument.damaged else instrument.name ),
                    required=False,
                    initial= self.instance.bookings.filter(instrument=instrument).exists() if self.instance else False,
                    )
    
    class Meta:
        model = Event
        widgets = {
                    'name': forms.TextInput(attrs={'placeholder':'e.g., UNISON and UNITE Strike Day', 'class':'span7'}),
                    'notes': forms.Textarea(attrs={'class':'span7', 'rows':'4'}),
                    'start': MySplitDateTimeWidget(attrs={'class':'datetimefield'}, date_placeholder="31/12/2011",
                                                                                    time_placeholder="12:00"),
                    }
    
    def instrument_fields(self):
        return [field for field in self if field.field.__class__ == forms.BooleanField]
    
    def non_instrument_fields(self):
        return [field for field in self if field.field.__class__ != forms.BooleanField]
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        if name == self.instance.name:
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
                    Booking.objects.get_or_create(instrument=Instrument.objects.get(name=field.name), event=event)
                else:
                    try:
                        Booking.objects.get(instrument=Instrument.objects.get(name=field.name), event=event).delete()
                    except Booking.DoesNotExist:
                        continue
        return event

class EventPlayersForm(forms.Form):
    def __init__(self, event=None, *args, **kwargs):
        super(EventPlayersForm, self).__init__(*args, **kwargs)
        self.event = event
        for b in self.event.bookings.all():
            self.fields[b.instrument.name] = forms.ModelChoiceField(
                            label=mark_safe(b.instrument.name),
                            queryset=UserProfile.objects.all(),
                            required=False,
                            initial=b.user.get_profile() if b.user else None,
                            )
    
    def save(self, commit=True):
        if commit:
            for field in self.fields:
                b = self.event.bookings.get(instrument=Instrument.objects.get(name=field))
                b.user = self.cleaned_data[field].user if self.cleaned_data[field] else None
                b.save()
        return None


class ContactForm(forms.Form):
    username = UserSignupForm().fields['username']
    username.widget.attrs['class'] = "span3"
    name = UserSignupForm().fields['name']
    name.widget.attrs['class'] = "span3"
    telephone = UserSignupForm().fields['telephone']
    telephone.widget.attrs['class'] = "span3"
    
    def __init__(self, instance=None, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.instance = instance
        self.fields['username'].initial = self.instance.username
        self.fields['name'].initial = self.instance.get_profile().name
        self.fields['telephone'].initial = self.instance.get_profile().telephone
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        if username == self.instance.username:
            return username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that email address already exists."))
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        if name == self.instance.get_profile().name:
            return name
        try:
            UserProfile.objects.get(slug=slugify(name))
        except UserProfile.DoesNotExist:
            return name
        raise forms.ValidationError(_("A user with that display name address already exists."))
    
    def save(self, commit=True):
        user = self.instance
        user.email = user.username = self.cleaned_data["username"]
        profile = self.instance.get_profile()
        profile.name = self.cleaned_data["name"]
        profile.telephone = self.cleaned_data["telephone"]
        if commit:
            user.save()
            profile.save()
        return user

class InstrumentNoteForm(forms.ModelForm):
    def __init__(self, event=None, instrument=None, user=None, *args, **kwargs):
        super(InstrumentNoteForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = InstrumentNote
        widgets = {'note': forms.Textarea(attrs={'class':'span9', 'rows':'4'})}


class AdminBookingSigninForm(forms.Form):
    def __init__(self, instrument=None, *args, **kwargs):
        super(AdminBookingSigninForm, self).__init__(*args, **kwargs)
        self.instrument = instrument
        self.fields['damaged'] = InstrumentForm(instance=self.instrument).fields['damaged']
        self.fields['booking'] = fields.BookingChoiceField(label=mark_safe("Booking after which instrument was returned"),
                                                            queryset=self.instrument.bookings.not_signed_in(),
                                                            empty_label=None, initial=instrument.get_last_booking(),)
    
    notes = InstrumentNoteForm().fields['note']
    notes.required = False

    def _get_note(self):
        return (" and wrote:</p><blockquote>%s</blockquote>"
                                % (linebreaks(escape(self.cleaned_data['notes'])),) if self.cleaned_data['notes'] else "")
    
    def get_booking(self):
        return self.cleaned_data['booking']
    
    def save(self, commit=True):
        booking = self.get_booking()
        if commit:
            booking.signed_in = True
            booking.save()
            booking.instrument.damaged = self.cleaned_data['damaged']
            booking.instrument.save()
            note = InstrumentNote(instrument=booking.instrument, user=booking.user, date_made=booking.event.start,
                                    note=str(booking) + self._get_note(), event=booking.event)
            note.save()
            for b in booking.instrument.bookings.not_signed_in().filter(event__start__lt=booking.event.start):
                b.signed_in = True
                b.save()
                note = InstrumentNote(instrument=b.instrument, user=b.user, date_made=b.event.start,
                                        note=str(b), event=b.event)
                note.save()
        return booking.instrument

class BookingSigninForm(AdminBookingSigninForm):
    def __init__(self, booking=None, *args, **kwargs):
        super(BookingSigninForm, self).__init__(instrument=booking.instrument, *args, **kwargs)
        self.fields.pop('booking')
        self.booking = booking
    
    def get_booking(self):
        return self.booking

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