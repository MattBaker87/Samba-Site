from django.dispatch import receiver
from django.conf import settings
from django.template.loader import render_to_string

from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from django.contrib.auth.models import User

def email_admins(subject, message, sender=settings.DEFAULT_FROM_EMAIL):
    for user in User.objects.filter(is_staff=True):
        user.email_user(subject, message, sender)

def inform_admins_of_registration(sender, **kwargs):
    if Site._meta.installed:
        site = Site.objects.get_current()
    else:
        site = RequestSite(kwargs['request'])
    
    ctx_dict = { 'user': kwargs['user'], 'site': site }
    subject = render_to_string('main/accounts/not_logged_in/signup_emails/registration_alert_email_subject.txt', ctx_dict)
    # Email subject *must not* contain newlines
    subject = settings.EMAIL_SUBJECT_PREFIX + ''.join(subject.splitlines())
    message = render_to_string('main/accounts/not_logged_in/signup_emails/registration_alert_email.txt', ctx_dict)
    
    email_admins(subject, message)

def inform_user_of_activation(sender, **kwargs):
    if Site._meta.installed:
        site = Site.objects.get_current()
    else:
        site = RequestSite(kwargs['request'])
    user = kwargs['user']
    
    ctx_dict = { 'user': user, 'site': site }
    subject = render_to_string('main/accounts/not_logged_in/signup_emails/activation_alert_email_subject.txt', ctx_dict)
    # Email subject *must not* contain newlines
    subject = settings.EMAIL_SUBJECT_PREFIX + ''.join(subject.splitlines())
    message = render_to_string('main/accounts/not_logged_in/signup_emails/activation_alert_email.txt', ctx_dict)

    user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
    
    