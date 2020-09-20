from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, primary_key=True)
    is_host = models.BooleanField(default=False)
    about = models.TextField(max_length=500)

