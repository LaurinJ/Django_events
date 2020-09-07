from django.db import models
from django.conf import settings

class EventManager(models.Manager):
    def filter_by_category(self, category):
        db_equivalent = ''
        for pair in self.model.CATEGORY_CHOICES:
            if pair[1] == category:
                db_equivalent = pair[0]
                break
        else:
            return self.all()
        return self.filter(category=db_equivalent)

class Event(models.Model):

    FUN = 'FN'
    RELAX = 'RX'
    EXP = 'EX'
    SIGHTS = 'SI'

    CATEGORY_CHOICES= (
        (FUN, 'fun'),
        (RELAX, 'relax'),
        (EXP, 'experience'),
        (SIGHTS, 'sights')
    )

    host = models.ForeignKey(settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE) 
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    location = models.CharField(max_length=500)
    
    category = models.CharField(
        max_length=20,
        choices = CATEGORY_CHOICES,
        default = FUN,
    )

    objects = EventManager()

    def __str__(self):
        return self.name

class EventRun(models.Model):

    event = models.ForeignKey(Event, 
        on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False)
    time = models.TimeField(blank=False, null=False)
    seats_available = models.PositiveIntegerField(blank=False, null=False)
    price = models.DecimalField(max_digits=10, 
        decimal_places=2, blank=False, null=False)

