from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from main.managers import BookingManager, EventManager, InstrumentManager

from django.contrib.sites.models import Site

from datetime import datetime, timedelta


####### Models #######

LONG = 500
SHORT = 100

class Event(models.Model):
    name = models.CharField(max_length=LONG)
    slug = models.SlugField(unique=True, editable=False)
    start = models.DateTimeField(verbose_name="When")
    location = models.CharField(max_length=LONG)
    coordinator = models.ForeignKey(User, related_name='coordinating', blank=True, null=True, default=None)
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
    
    def get_available(self):
        return self.bookings.filter(user=None)
    
    def get_label(self):
        x = self.get_sign_ups().count()
        if x < 10:
            return "important"
        elif x < 15:
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
    
    def get_coordinate_url(self):
        return ('event_coordinate', (), {'slug': self.slug})
    get_coordinate_url = models.permalink(get_coordinate_url)
    
    def get_cancel_coordinate_url(self):
        return ('event_cancel_coordinate', (), {'slug': self.slug})
    get_cancel_coordinate_url = models.permalink(get_cancel_coordinate_url)

class Instrument(models.Model):
    INSTRUMENT_CHOICES = (
        ('agog', 'Agogo'),
        ('caix', 'Caixa'),
        ('repi', 'Repinique'),
        ('shak', 'Shaker'),
        ('sur1', 'Surdo (low)'),
        ('sur2', 'Surdo (mid)'),
        ('sur3', 'Surdo (high)'),
        ('tamb', 'Tamborim'),
        )
    
    slug = models.SlugField(unique=True, editable=False)
    instrument_type = models.CharField(max_length=4, choices=INSTRUMENT_CHOICES, verbose_name="Instrument type")
    name = models.CharField(max_length=SHORT, verbose_name="Instrument name")
    damaged = models.BooleanField(default=False, verbose_name="This instrument is damaged")
    is_removed = models.BooleanField(default=False, editable=False, verbose_name="Removed from website")
    
    class Meta:
        ordering = ['instrument_type', 'name']
    
    objects = models.Manager()
    live = InstrumentManager()
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Instrument, self).save(*args, **kwargs)
    
    ########## Get status ###########  
    def get_signed_in(self):
        return not self.bookings.not_signed_in().exists()
    
    ########## Remove instrument (and clean up past and future bookings) ##########
    
    def do_remove(self):
        self.is_removed = True
        self.save()
        for b in self.bookings.future_bookings():       # Delete future bookings
            b.delete()
        for b in self.bookings.not_signed_in():         # Delete bookings that weren't signed in. Feels wrong...
            b.delete()
        return ''
    
    ########## Related bookings, notes and users ##########
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
    
    def get_next_needed_date(self):
        return self.get_next_booking().event.start if self.get_next_booking() else datetime.now() + timedelta(10000)
    
    def get_users_since_signed_in(self):
        return User.objects.filter(id__in=[b.user.id for b in self.bookings.not_signed_in()])
    
    def get_removed_note(self):
        x = self.user_notes.filter(subject="remove")
        return x[0] if x else None
    
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

    def get_resurrect_url(self):
        return ('instrument_resurrect', (), {'slug': self.slug})
    get_resurrect_url = models.permalink(get_resurrect_url)
    
    def get_signin_url(self):
        return ('instrument_signin_admin', (), {'slug': self.slug})
    get_signin_url = models.permalink(get_signin_url)
    
    def get_note_url(self):
        return ('instrument_write_note', (), {'slug': self.slug})
    get_note_url = models.permalink(get_note_url)
    
    def get_repair_url(self):
        return ('instrument_repair', (), {'slug': self.slug})
    get_repair_url = models.permalink(get_repair_url)
    
    def get_damage_url(self):
        return ('instrument_damage', (), {'slug': self.slug})
    get_damage_url = models.permalink(get_damage_url)
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    telephone = models.CharField(max_length=15, blank=True)
    slug = models.SlugField(unique=True, editable=False)
    
    class Meta:
        ordering = ['name']

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
        return "%s played '%s' at %s" % (self.user.get_profile().get_linked_name(),
                                        self.instrument.name,
                                        self.event.get_linked_name())
    
    ################ URLs and links #################
    def get_absolute_url(self):
        return ('event_detail', (), {'slug': self.event.slug})
    get_absolute_url = models.permalink(get_absolute_url)
    
    def get_book_url(self):
        return ('instrument_sign_out', (), {'pk': self.id})
    get_book_url = models.permalink(get_book_url)
    
    def get_cancel_url(self):
        return ('cancel_sign_out', (), {'pk': self.id})
    get_cancel_url = models.permalink(get_cancel_url)
    
    def get_signin_url(self):
        return ('instrument_booking_signin', (), {'booking_id': self.id})
    get_signin_url = models.permalink(get_signin_url)


class InstrumentNote(models.Model):
    NOTE_CHOICES =(
        ('damage', 'Flagged as damaged'),
        ('repair', 'Flaged as no longer damaged'),
        ('general', 'General note'),
        ('event', 'Played at event'),
        ('rename', 'Renamed'),
        ('type', 'Type changed'),
        ('added', 'Added'),
        ('remove', 'Removed'),
        ('resurrect', 'Resurrected')
        )
    
    instrument = models.ForeignKey(Instrument, related_name='user_notes', blank=False, null=False, editable=False)
    user = models.ForeignKey(User, related_name='instrument_notes', blank=False, null=False, editable=False)
    event = models.ForeignKey(Event, related_name='user_notes', blank=True, null=True, default=None, editable=False)
    date_made = models.DateTimeField(editable=False)
    note = models.TextField(verbose_name="Notes on the instrument", blank=True)
    is_editable = models.BooleanField(editable=False, default=False)
    is_removed = models.BooleanField(editable=False, default=False, verbose_name="Removed from website")
    subject = models.CharField(max_length=10, choices=NOTE_CHOICES)
    
    class Meta:
        ordering = ['-date_made']
    
    ################ Display of notes ################
    def get_booking(self):
        return Booking.objects.get(instrument=self.instrument, user=self.user, event=self.event) if self.event else None
    
    def get_note_display(self):
        display_options = {'damage':"<p>%s marked '%s' as damaged and wrote:</p><blockquote>%s</blockquote>" % (
                        self.user.get_profile().get_linked_name(), self.instrument.name, self.note) if self.note else \
                        "<p>%s marked '%s' as damaged</p>" % (self.user.get_profile().get_linked_name(), \
                                                                            self.instrument.name),
            'repair':"<p>%s marked '%s' as repaired and wrote:</p><blockquote>%s</blockquote>" % (
                        self.user.get_profile().get_linked_name(), self.instrument.name, self.note) if self.note else \
                        "<p>%s marked '%s' as repaired</p>" % (self.user.get_profile().get_linked_name(), \
                                                                            self.instrument.name),
            'general':'<p>%s wrote:</p><blockquote>%s</blockquote>' % (self.user.get_profile().get_linked_name(), self.note),
            'event':'<p>%s and wrote:</p><blockquote>%s</blockquote>' % (unicode(self.get_booking()), self.note) if self.note \
                                                                            else '<p>%s</p>' % unicode(self.get_booking()),
            'rename':'<p>%s renamed the instrument %s</p>' % (self.user.get_profile().get_linked_name(), self.note),
            'type':"<p>%s changed the type of '%s' %s</p>" % (self.user.get_profile().get_linked_name(), self.instrument.name, \
                                                                            self.note),
            'added':"<p>%s added '%s'</p>" % (self.user.get_profile().get_linked_name(), self.instrument.name),
            'remove':"<p>%s marked '%s' as no longer in the band's possession and wrote:</p><blockquote>%s</blockquote>" % (
                        self.user.get_profile().get_linked_name(), self.instrument.name, self.note) if self.note else \
                        "<p>%s marked '%s' as no longer in the band's possession</p>" % (self.user.get_profile().get_linked_name(),
                                                                                        self.instrument.name),
            'resurrect':"<p>%s marked '%s' as back in the band's possession and wrote:</p><blockquote>%s</blockquote>" % (
                        self.user.get_profile().get_linked_name(), self.instrument.name, self.note) if self.note else \
                        "<p>%s marked '%s' as back in the band's possession</p>" % (self.user.get_profile().get_linked_name(),
                                                                                        self.instrument.name),
            }
    
        return display_options[self.subject]
        
        
    ################ URLs ##############
    
    def get_delete_url(self):
        return ('remove_note', (), {'pk': self.id})
    get_delete_url = models.permalink(get_delete_url)