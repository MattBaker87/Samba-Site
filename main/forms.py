from datetime import datetime

from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from django.forms.widgets import TextInput, PasswordInput, Textarea
from main.widgets import MySplitDateTimeWidget

from main import fields

from django.contrib.auth.models import User
from main.models import UserProfile, Instrument, Event, Booking

class UserSignupForm(forms.ModelForm):
    username = forms.EmailField(label=_("Email"), max_length=30,
        help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': _("Please enter a valid email address. It should be 30 characters or fewer."),
                            'required': _("You didn't enter an email address. We need that!")},
        widget = TextInput(attrs={'placeholder':'Email', 'label':'email'}))
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput(attrs={'placeholder':'Password', 'label':'password'}),
        error_messages = {'required': _("You didn't enter a password. You need a password!")})
    password2 = forms.CharField(label=_("Password confirmation"),
        help_text = _("Enter the same password as above, for verification."),
        error_messages = {'required': _("You didn't confirm your password. There could be typos.")},
        widget=forms.PasswordInput(attrs={'placeholder':'Password (check)', 'label':'password_again'}))
    name = forms.CharField(label=_("Name"), max_length=30,
        help_text = _("This is the name you'll be known as on the site."),
        error_messages = {'required': _("You didn't enter a display name. We need that!")},
        widget = TextInput(attrs={'placeholder':'Display name', 'label':'name'}))
    telephone = fields.UKPhoneNumberField(reject=(None, 'premium', 'service'),
        help_text = _("Required. We use this to help organise, and to chase down drums."),
        error_messages = {'required': _("You didn't enter a phone number. We need that!")},
        widget = TextInput(attrs={'placeholder':'Mobile phone number', 'label':'telephone'}))
    
    class Meta:
        model = User
        fields = ("username",)
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that email address already exists."))
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        try:
            UserProfile.objects.get(name=name)
        except UserProfile.DoesNotExist:
            return name
        raise forms.ValidationError(_("A user with that display name address already exists."))
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two passwords you entered didn't match."))
        return password2
    
    def save(self, commit=True):
        user = User(username=self.cleaned_data["username"], email=self.cleaned_data["username"])
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            profile = UserProfile(user=user, name=self.cleaned_data["name"], telephone=self.cleaned_data["telephone"])
            profile.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_("Username"), max_length=30,
                                widget=TextInput(attrs={'placeholder':'Email', 'label':'email'}))
    password = forms.CharField(label=_("Password"), max_length=30,
                                widget=PasswordInput(attrs={'placeholder':'Password', 'label':'password'}))
    
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
        widgets = {'name': TextInput(attrs={'placeholder':'Agogo 1 (example)'}),}
        exclude = ['slug']
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        try:
            Instrument.objects.get(slug=slugify(name))
        except Instrument.DoesNotExist:
            return name
        raise forms.ValidationError(_("Instrument already exists"))


class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        for instrument in Instrument.objects.all():
            self.fields[instrument.name] = forms.BooleanField(
                            label=mark_safe(instrument.name +
                                ' <span class="label important">Damaged</span>' if instrument.damaged else instrument.name ),
                            required=False
                            )
    
    class Meta:
        model = Event
        widgets = {
                    'name': TextInput(attrs={'placeholder':'e.g., UNISON and UNITE Strike Day', 'class':'span7'}),
                    'notes': Textarea(attrs={'class':'span7', 'rows':'4'}),
                    }
        exclude = ['slug']
     
    when = forms.DateTimeField(label=_("When"),
        help_text = _("Use dd/mm/yyyy, hh:mm format"),
        widget = MySplitDateTimeWidget(attrs={'class':'datetimefield'}, date_placeholder="31/12/2011", time_placeholder="12:00"))
    
    def instrument_fields(self):
        return [field for field in self if field.field.__class__ == forms.BooleanField]
    
    def non_instrument_fields(self):
        return [field for field in self if field.field.__class__ != forms.BooleanField]
    
    def clean_name(self):
        name = self.cleaned_data["name"]
        try:
            Event.objects.get(slug=slugify(name))
        except Event.DoesNotExist:
            return name
        raise forms.ValidationError(_("An event with that name already exists"))
    
    def clean_when(self):
        when = self.cleaned_data["when"]
        if when <= datetime.now():
            raise forms.ValidationError(_("Please enter a date in the future"))
        return when
        
    
    def save(self, commit=True):
        event = super(EventForm, self).save(commit=False)
        if commit:
            event.save()
            for field in self.instrument_fields():
                if self.cleaned_data[field.name]:
                    Booking.objects.create(instrument=Instrument.objects.get(name=field.name), event=event)
        return event

class ContactForm(forms.ModelForm):
    username = forms.EmailField(label=_("Email"), max_length=30,
        help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': _("Please enter a valid email address. It should be 30 characters or fewer."),
                            'required': _("You didn't enter an email address. We need that!")},
        widget = TextInput(attrs={'placeholder':'Email', 'label':'email'}))
    name = forms.CharField(label=_("Name"), max_length=30,
        help_text = _("This is the name you'll be known as on the site."),
        error_messages = {'required': _("You didn't enter a display name. We need that!")},
        widget = TextInput(attrs={'placeholder':'Display name', 'label':'name'}))
    telephone = fields.UKPhoneNumberField(reject=(None, 'premium', 'service'),
        help_text = _("Required. We use this to help organise, and to chase down drums."),
        error_messages = {'required': _("You didn't enter a phone number. We need that!")},
        widget = TextInput(attrs={'placeholder':'Mobile phone number', 'label':'telephone'}))
    
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = kwargs['instance'].username
        self.fields['name'].initial = kwargs['instance'].get_profile().name
        self.fields['telephone'].initial = kwargs['instance'].get_profile().telephone
    
    class Meta:
        model = User
        fields = ("username",)
    
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
            UserProfile.objects.get(name=name)
        except UserProfile.DoesNotExist:
            return name
        raise forms.ValidationError(_("A user with that display name address already exists."))
    
    def save(self, commit=True):
        user = self.instance
        profile = self.instance.get_profile()
        profile.name = self.cleaned_data["name"]
        profile.telephone = self.cleaned_data["telephone"]
        user.email = user.username = self.cleaned_data["username"]
        if commit:
            user.save()
            profile.save()
        return user