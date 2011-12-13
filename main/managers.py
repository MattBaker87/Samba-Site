from django.db import models

from datetime import datetime

class BookingManager(models.Manager):    
    def signed_up(self):
	    return self.exclude(user=None)
	
    def display(self):
	    return self.exclude(user=None, event__start__lt=datetime.now())
	
    def future_bookings(self):
	    return self.filter(event__start__gte=datetime.now()).order_by('event__start')
	
    def past_bookings(self):
	    return self.filter(event__start__lt=datetime.now()).order_by('-event__start')
	
    def not_signed_in(self):
	    return self.filter(event__start__lt=datetime.now(), signed_in=False).order_by('-event__start')
	
    def label(self):
	    if self.exclude(user=None).count() < 5:
	        return "important"
	    elif self.count() < 10:
	        return "warning"
	    else:
	        return "success"

class EventManager(models.Manager):
    def future_events(self):
        return self.filter(start__gte=datetime.now())

    def past_events(self):
        return self.filter(start__lt=datetime.now())