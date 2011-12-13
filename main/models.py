from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from main.managers import BookingManager, EventManager

from datetime import datetime

LONG = 500
SHORT = 100

class Event(models.Model):
    name = models.CharField(max_length=LONG)
    slug = models.SlugField(unique=True)
    start = models.DateTimeField()
    location = models.CharField(max_length=LONG)
    notes = models.CharField(max_length=LONG)
    
    objects = EventManager()
    
    class Meta:
        ordering = ['start']
    
    def get_absolute_url(self):
        return ('event_detail', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)
    
    def get_delete_url(self):
        return ('event_delete', (), {'slug': self.slug})
    get_delete_url = models.permalink(get_delete_url)
    
    def get_edit_url(self):
        return ('event_edit', (), {'slug': self.slug})
    get_edit_url = models.permalink(get_edit_url)
    
    def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Event, self).save(*args, **kwargs)

class Instrument(models.Model):
    INSTRUMENT_CHOICES = (
        ('agog', 'Agogo'),
        ('caix', 'Caixa'),
        ('repi', 'Repinique'),
        ('shak', 'Shaker'),
        ('sur1', 'Surdo 1'),
        ('sur2', 'Surdo 2'),
        ('sur3', 'Surdo 3'),
        ('tamb', 'Tamborim'),
        )
    
    slug = models.SlugField(unique=True)
    instrument_type = models.CharField(max_length=4, choices=INSTRUMENT_CHOICES, verbose_name="Instrument type")
    name = models.CharField(max_length=SHORT, verbose_name="Instrument name")
    damaged = models.BooleanField(default=False, verbose_name="This instrument is damaged")
    
    class Meta:
        ordering = ['instrument_type', 'name']
    
    def __unicode__(self):
        return self.name
        
    def past_bookings(self):
        return self.bookings.exclude(user__isnull=True).filter(event__start__lte=datetime.now()).order_by('-event__start')
    
    def future_bookings(self):
        return self.bookings.exclude(user__isnull=True).filter(event__start__gte=datetime.now()).order_by('event__start')
    
    def last_booking(self):
        x = self.past_bookings()
        if x:
            return x[0]
        else:
            return None
    
    def next_booking(self):
        x = self.future_bookings()
        if x:
            return x[0]
        else:
            return None
    
    def location(self):
        x = self.last_booking()
        if x and x.signed_in == False:
            return "Not yet signed back in"
        else:
            return "Store room"
    
    def get_absolute_url(self):
        return ('instrument_detail', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)

    def get_edit_url(self):
        return ('instrument_edit', (), {'slug': self.slug})
    get_edit_url = models.permalink(get_edit_url)
    
    def get_delete_url(self):
        return ('instrument_delete', (), {'slug': self.slug})
    get_delete_url = models.permalink(get_delete_url)
    
    def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Instrument, self).save(*args, **kwargs)
        

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    name = models.CharField(max_length=SHORT, unique=True)
    telephone = models.CharField(max_length=15, blank=True)
    slug = models.SlugField(unique=True)
    
    def get_upcoming_events(self):
        seen = set()
        t = []
        for x in self.user.bookings.future_bookings():
            if not x.event in seen:
                x.event.user_bookings = []
                t.append(x.event)
                seen.add(x.event)
            t[t.index(x.event)].user_bookings.append(x)
        return t
    
    def get_past_events(self):
        seen = set()
        t = []
        for x in self.user.bookings.past_bookings():
            if not x.event in seen:
                x.event.user_bookings = []
                t.append(x.event)
                seen.add(x.event)
            t[t.index(x.event)].user_bookings.append(x)
        return t
    
    def next_booking(self):
        x = self.user.bookings.future_bookings()
        if x:
            return x[0]
        else:
            return None
    
    def last_booking(self):
        x = self.user.bookings.past_bookings()
        if x:
            return x[0]
        else:
            return None
    
    def get_absolute_url(self):
        return ('view_profile', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)

    def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(UserProfile, self).save(*args, **kwargs)

class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', blank=True, null=True, default=None)
    instrument = models.ForeignKey('Instrument', related_name='bookings')
    event = models.ForeignKey('Event', related_name='bookings')
    signed_in = models.BooleanField(default=False, verbose_name="This instrument is back in the store room")
    
    objects = BookingManager()
    
    class Meta:
        ordering = ['instrument']
    
    def make_booking_url(self):
        return ('instrument_sign_out', (), {'booking_id': self.id})
    make_booking_url = models.permalink(make_booking_url)
    
    def cancel_booking_url(self):
        return ('cancel_sign_out', (), {'booking_id': self.id})
    cancel_booking_url = models.permalink(cancel_booking_url)
    
    def get_signin_url(self):
        return ('instrument_signin', (), {'booking_id': self.id})
    get_signin_url = models.permalink(get_signin_url)