from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Max, F
from django.db.models.aggregates import Max
from django.utils.text import slugify
from django.urls import reverse

class EventQuerySet(models.QuerySet):
    def filter_by_category(self, category=None):
        db_equivalent = ''
        for pair in self.model.CATEGORY_CHOICES:
            if pair[1] == category:
                db_equivalent = pair[0]
                break
        else:
            return self.all()
        return self.filter(category=db_equivalent)

    # def filter_available(self, date_from=None, date_to=None, guests=None):
    #     date_from = date_from or timezone.now().date()
    #     qs = self.annotate(max_seats=Max('eventrun__seats_available'))
    #
    #     if date_to:
    #         qs = qs.filter(eventrun__date__range=(date_from, date_to))
    #     else:
    #         qs = qs.filter(eventrun__date__gte=date_from)
    #     if guests:
    #         qs = qs.filter(max_seats__gte=guests)
    #
    #     return qs

    def filter_available(self, date_from=None, date_to=None, guests=None):
        # filter first all the eventruns and then get the ids to events
        date_from = date_from or timezone.now().date()

        if date_to:
            qs = EventRun.objects.filter(date__range=(date_from, date_to))
        else:
            qs = EventRun.objects.filter(date__gte=date_from)
        if guests:
            qs = qs.filter(seats_available__gte=guests)
        return self.filter(pk__in=qs.values_list('event', flat=True))

class EventManager(models.Manager):

    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)

    def search(self, query=None):
        lookup = (
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
        )
        return self.filter(lookup).distinct()

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
    slug = models.SlugField(max_length=200, unique=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    
    category = models.CharField(
        max_length=20,
        choices = CATEGORY_CHOICES,
        default = FUN,
    )

    objects = EventManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('events:detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name + '-with-' + self.host.username)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        unique_together = (("name", "host"),)

class EventRun(models.Model):

    event = models.ForeignKey(Event, 
        on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False)
    time = models.TimeField(blank=False, null=False)
    seats_available = models.PositiveIntegerField(blank=False, null=False)
    price = models.DecimalField(max_digits=10, 
        decimal_places=2, blank=False, null=False)

