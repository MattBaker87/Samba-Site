from django.db import models
from django.contrib.auth.models import User

LONG = 500
SHORT = 100

class Event(models.Model):
    name = models.CharField(max_length=LONG)
    location = models.CharField(max_length=LONG)
    when = models.DateTimeField()
    notes = models.CharField(max_length=LONG)
    
    class Meta:
        ordering = ['when']

class Instrument(models.Model):
    name = models.CharField(max_length=SHORT)
    damaged = models.BooleanField(default=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=SHORT, blank=True)
    telephone = models.CharField(max_length=15, blank=True)

class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings')
    instrument = models.ForeignKey('Instrument', related_name='bookings')
    event = models.ForeignKey('Event', related_name='bookings')
    
    class Meta:
        ordering = ['instrument']