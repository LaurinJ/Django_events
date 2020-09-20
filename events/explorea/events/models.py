from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Max, F
from django.db.models.aggregates import Max
from django.utils.text import slugify
from django.urls import reverse

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


def get_related_attr(obj, attrs):
    related_obj = obj
    for attr in attrs:
        related_obj = getattr(related_obj, attr)
    return related_obj

def thumbnail_image_url(instance, filename):
    '''upload_to for Event thumbnail image'''
    return 'user_{0}/thumb_{1}'.format(instance.host.id, filename)

def main_image_url(instance, filename):
    '''upload_to for Event main image'''
    return 'user_{0}/main_{1}'.format(instance.host.id, filename)

def album_image_url(instance, filename):
    '''upload_to for Image model'''
    return 'user_{0}/{1}/{2}'.format(instance.album.event.host.id,
        instance.album.title, filename)

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


class EventRunQuerySet(models.QuerySet):

    def filter_by_category(self, category=None):
        db_equivalent = ''
        for pair in Event.CATEGORY_CHOICES:
            if pair[1] == category:
                db_equivalent = pair[0]
                break
        else:
            return self.all()

        return self.filter(event__category=db_equivalent)

    def filter_available(self, date_from=None, date_to=None, guests=None):
        # filter first all the eventruns and then get the ids to events
        date_from = date_from or timezone.now().date()

        if date_to:
            qs = self.filter(date__range=(date_from, date_to))
        else:
            qs = self.filter(date__gte=date_from)

        if guests:
            qs = qs.filter(seats_available__gte=guests)

        return qs

    def filter_first_available(self, date_from=None, date_to=None, guests=None, sort_by='date'):

        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            qs = self.filter_available(date_from, date_to, guests)
            qs = qs.order_by('event_id', 'date', 'time').distinct('event_id')
            return qs

        qs = self.filter_available(date_from, date_to, guests).order_by('date', 'time')

        event_ids = []
        filtered = []
        for run in qs:
            if not run.event.id in event_ids:
                filtered.append(run)
                event_ids.append(run.event.id)

        reverse, fields = (sort_by.startswith('-'), sort_by.lstrip('-').split('__'))

        criterion = lambda obj: get_related_attr(obj, fields)

        result = sorted(filtered, key=criterion, reverse=reverse)
        return result


class EventRunManager(models.Manager):

    def get_queryset(self):
        return EventRunQuerySet(self.model, using=self._db)

    def search(self, query=None):
        lookup = (
                Q(event__name__icontains=query) |
                Q(event__description__icontains=query) |
                Q(event__location__icontains=query)
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

    thumbnail = ProcessedImageField(upload_to=thumbnail_image_url,
                                    processors=[ResizeToFill(300, 200)],
                                    format='PNG',
                                    options={'quality': 60},
                                    null=True)
    main_image = ProcessedImageField(upload_to=main_image_url,
                                     processors=[ResizeToFill(500, 600)],
                                     format='PNG',
                                     options={'quality': 100},
                                     null=True)

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

        if not hasattr(self, 'album'):
            Album.objects.create(event=self)

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

    objects = EventRunManager()

class Album(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = "album_" + self.event.name
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.title)

class Image(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = ProcessedImageField(upload_to=album_image_url,
            processors=[ResizeToFill(500,400)],
            format='PNG',
            options={'quality':80})
    title = models.CharField(max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}/{}'.format(self.album, self.title)

    class Meta:
        ordering = ['created']