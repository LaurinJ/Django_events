from django.db import models
from django.conf import settings


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    location = models.CharField(max_length=500)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    category = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class EventRun(models.Model):
    event = models.ForeignKey(Event,
        on_delete=models.CASCADE)
    happens = models.DateTimeField(blank=False, null=False)
    seats_available = models.PositiveIntegerField(blank=False, null=False)
    price = models.DecimalField(max_digits=10,
        decimal_places=2, blank=False, null=False)