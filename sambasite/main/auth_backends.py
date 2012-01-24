import re

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration import signals
from registration.models import RegistrationProfile
from registration.backends.default import DefaultBackend

from main.models import UserProfile

from main.receivers import inform_admins_of_registration
from main.receivers import inform_user_of_activation

########## Connect signals related to backends ##########
signals.user_registered.connect(inform_admins_of_registration)
signals.user_activated.connect(inform_user_of_activation)


class AuthWithEmailBackend(ModelBackend):
    """
    Allows users to log in using their email address instead of their username.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

class RegistrationBackend(DefaultBackend):
    """
    Used in django-registration. Creates user profile and cancels default email to membership applicants. Signal sent
    is used to send an email to all admins alerting them of a new membership request.
    """
    def register(self, request, **kwargs):
        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email, password, site, send_email=False)
        profile = UserProfile.objects.create(user=new_user, name=kwargs["name"], telephone=kwargs["telephone"])
        
        signals.user_registered.send(sender=self.__class__, user=new_user, request=request)
        
        return new_user
    