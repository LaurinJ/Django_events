from .models import Profile

from django.core.signals import request_finished
from django.dispatch import receiver

def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(request_finished)
def my_callback(sender, **kwargs):
    print("Request finished!")