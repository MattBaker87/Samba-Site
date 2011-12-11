from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.template.defaultfilters import slugify

from django.forms.widgets import TextInput, PasswordInput

from main import fields

from django.contrib.auth.models import User
from main.models import UserProfile, Instrument, Event

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
        raise forms.ValidationError(_("An instrument with that name address already exists"))

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        widgets = {'name': TextInput(attrs={'placeholder':'UNISON and UNITE Strike Day (example)'}),}
        exclude = ['slug']

    def clean_name(self):
        name = self.cleaned_data["name"]
        try:
            Event.objects.get(slug=slugify(name))
        except Event.DoesNotExist:
            return name
        raise forms.ValidationError(_("An event with that name address already exists"))