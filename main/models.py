from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from datetime import datetime

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
    INSTRUMENT_CHOICES = (
        ('surd', 'Surdo'),
        ('agog', 'Agogo'),
        ('caix', 'Caixa'),
        ('repi', 'Repinique'),
        ('tamb', 'Tamborim'),
        ('shak', 'Shaker'),
        )
    
    slug = models.SlugField(unique=True, primary_key=True)
    instrument_type = models.CharField(max_length=4, choices=INSTRUMENT_CHOICES, verbose_name="Instrument type")
    name = models.CharField(max_length=SHORT, verbose_name="Instrument name")
    damaged = models.BooleanField(default=False, verbose_name="This instrument is damaged")
    
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
        
    def past_bookings(self):
        return self.bookings.exclude(user__isnull=True).filter(event__when__gte=datetime.now()).order_by('-event__when')
    
    def future_bookings(self):
        return self.bookings.exclude(user__isnull=True).filter(event__when__lte=datetime.now()).order_by('event__when')
    
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
            return mark_safe(x.user.name+" has not yet signed this back in (signed out "+x.event.when+")")
        else:
            return "Store room"
    
    def get_absolute_url(self):
        return ('instrument_detail', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)
    
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

class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', blank=True)
    instrument = models.ForeignKey('Instrument', related_name='bookings')
    event = models.ForeignKey('Event', related_name='bookings')
    signed_in = models.BooleanField(default=False, verbose_name="This instrument is back in the store room")
    
    class Meta:
        ordering = ['instrument']