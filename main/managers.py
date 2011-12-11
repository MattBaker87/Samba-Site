from django.db import models

import datetime

class BookingManager(models.Manager):
	def signed_up(self):
		return self.exclude(user=None)
