from django.db import models

from datetime import datetime

class BookingManager(models.Manager):    
    def future_bookings(self):
	    return self.filter(event__start__gte=datetime.now()).order_by('event__start')
	
    def past_bookings(self):
	    return self.filter(event__start__lt=datetime.now()).order_by('-event__start')
	
    def not_signed_in(self):
	    return self.filter(event__start__lt=datetime.now(), signed_in=False).exclude(user=None).order_by('event__start')

class EventManager(models.Manager):
    def future_events(self):
        return self.filter(start__gte=datetime.now())

    def past_events(self):
        return self.filter(start__lt=datetime.now())

class InstrumentManager(models.Manager):
    def get_query_set(self):
        return super(InstrumentManager, self).get_query_set().exclude(is_removed=True)

    def mia(self, user=None):
        if user:
            temp_ids = [i.id for i in self.get_query_set() if i.bookings.not_signed_in().filter(user=user).exists() \
                                                                                            and i.get_mia()]
        else:
            temp_ids = [i.id for i in self.get_query_set() if i.get_mia()]
        return self.get_query_set().filter(id__in=temp_ids)
    
    def just_played(self, user=None):
        if user:
            temp_ids = [i.id for i in self.get_query_set() if i.bookings.not_signed_in().filter(user=user).exists() \
                                                                                            and i.get_just_played()]
        else:
            temp_ids = [i.id for i in self.get_query_set() if i.get_just_played()]
        return self.get_query_set().filter(id__in=temp_ids)
    
    def not_signed_in(self, user=None):
        if user:
            temp_ids = [i.id for i in self.get_query_set() if i.bookings.not_signed_in().filter(user=user).exists()]
        else:
            temp_ids = [i.id for i in self.get_query_set() if i.bookings.not_signed_in().exists()]
        return self.get_query_set().filter(id__in=temp_ids)
