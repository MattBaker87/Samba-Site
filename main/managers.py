from django.db import models

from datetime import datetime

class BookingManager(models.Manager):
	def signed_up(self):
		return self.exclude(user=None)
	
	def display(self):
	    return self.exclude(user=None, event__when__lt=datetime.now())
	
	def future_bookings(self):
	    return self.filter(event__when__gte=datetime.now()).order_by('event__when')
	
	def past_bookings(self):
	    return self.filter(event__when__lt=datetime.now()).order_by('-event__when')

class EventManager(models.Manager):
    def future_events(self):
        return self.filter(when__gte=datetime.now())

    def past_events(self):
        return self.filter(when__lt=datetime.now())