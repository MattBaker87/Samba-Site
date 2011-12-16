from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from main.managers import BookingManager, EventManager

from django.contrib.sites.models import Site

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
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Event, self).save(*args, **kwargs)
    
    ########### Related bookings and info ###########
    def get_sign_ups(self):
        return self.bookings.exclude(user=None)
    
    def get_label(self):
        x = self.get_sign_ups().count()
        if x < 5:
            return "important"
        elif x < 10:
            return "warning"
        else:
            return "success"
    
    ############ URLs and links ##############
    def get_absolute_url(self):
        return ('event_detail', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)
    
    def get_linked_name(self):
        return mark_safe('<a href="'+self.get_absolute_url()+'">'+self.name+'</a>')
    
    def get_delete_url(self):
        return ('event_delete', (), {'slug': self.slug})
    get_delete_url = models.permalink(get_delete_url)
    
    def get_edit_url(self):
        return ('event_edit', (), {'slug': self.slug})
    get_edit_url = models.permalink(get_edit_url)
    
    def get_edit_players_url(self):
        return ('event_edit_players', (), {'slug': self.slug})
    get_edit_players_url = models.permalink(get_edit_players_url)


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

    def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Instrument, self).save(*args, **kwargs)
    
    ########## Get status ###########  
    def get_signed_in(self):
        return not self.bookings.not_signed_in().exists()
    
    ########## Related bookings and users ##########
    def get_past_bookings(self):
        return self.bookings.exclude(user__isnull=True).filter(event__start__lte=datetime.now()).order_by('-event__start')
    
    def get_future_bookings(self):
        return self.bookings.exclude(user__isnull=True).filter(event__start__gte=datetime.now()).order_by('event__start')
    
    def get_last_booking(self):
        x = self.get_past_bookings()
        return x[0] if x else None
    
    def get_next_booking(self):
        x = self.get_future_bookings()
        return x[0] if x else None
    
    def get_users_since_signed_in(self):
        return User.objects.filter(id__in=[b.user.id for b in self.bookings.not_signed_in()])

    ########## URLS and links ##########
    def get_absolute_url(self):
        return ('instrument_detail', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)

    def get_linked_name(self):
        return mark_safe('<a href="'+self.get_absolute_url()+'">'+self.name+'</a>')

    def get_edit_url(self):
        return ('instrument_edit', (), {'slug': self.slug})
    get_edit_url = models.permalink(get_edit_url)
    
    def get_delete_url(self):
        return ('instrument_delete', (), {'slug': self.slug})
    get_delete_url = models.permalink(get_delete_url)

    def get_signin_url(self):
        return ('instrument_signin_admin', (), {'slug': self.slug})
    get_signin_url = models.permalink(get_signin_url)
        

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    name = models.CharField(max_length=SHORT, unique=True)
    telephone = models.CharField(max_length=15, blank=True)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
    	return self.name
    
    def save(self, *args, **kwargs):
    	self.slug = slugify(self.name)
    	super(UserProfile, self).save(*args, **kwargs)
    
    ############# Related bookings ##############
    def get_future_events(self):
        return Event.objects.filter(id__in=[b.event.id for b in self.user.bookings.future_bookings()])
    
    def get_past_events(self):
        return Event.objects.filter(id__in=[b.event.id for b in self.user.bookings.past_bookings()])
    
    def get_next_booking(self):
        x = self.user.bookings.future_bookings()
        return x[0] if x else None
    
    def get_last_booking(self):
        x = self.user.bookings.past_bookings()
        return x[0] if x else None
    
    ############### URLs and links ###############
    def get_absolute_url(self):
        return ('view_profile', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)

    def get_linked_name(self):
        return mark_safe('<a href="'+self.get_absolute_url()+'">'+self.name+'</a>')
    
    def get_past_events_url(self):
        return ('profile_past_events', (), {'slug': self.slug})
    get_past_events_url = models.permalink(get_past_events_url)


class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', blank=True, null=True, default=None)
    instrument = models.ForeignKey('Instrument', related_name='bookings')
    event = models.ForeignKey('Event', related_name='bookings')
    signed_in = models.BooleanField(default=False, verbose_name="This instrument is back in the store room")
    
    objects = BookingManager()
    
    class Meta:
        ordering = ['instrument']
    
    def __unicode__(self):
        return "%s played %s at %s" % (self.user.get_profile().get_linked_name(),
                                        self.instrument.get_linked_name(),
                                        self.event.get_linked_name())
    
    ################ URLs and links #################
    def get_book_url(self):
        return ('instrument_sign_out', (), {'booking_id': self.id})
    get_book_url = models.permalink(get_book_url)
    
    def get_cancel_url(self):
        return ('cancel_sign_out', (), {'booking_id': self.id})
    get_cancel_url = models.permalink(get_cancel_url)
    
    def get_signin_url(self):
        return ('instrument_booking_signin', (), {'booking_id': self.id})
    get_signin_url = models.permalink(get_signin_url)


class InstrumentNote(models.Model):
    instrument = models.ForeignKey(Instrument, related_name='notes', blank=False, null=False)
    user = models.ForeignKey(User, related_name='instrument_notes', blank=False, null=False)
    booking = models.ForeignKey(Booking, related_name='notes', blank=True, null=True, default=None)
    date_made = models.DateTimeField(editable=False)
    note = models.TextField()
    
    class Meta:
        ordering = ['-date_made']