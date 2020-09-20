from django.db import models
from django.conf import settings
from django.urls import reverse

def image_dir(instance, filename):
    return 'user_{}/profile_{}'.format(instance.user.id, filename)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, primary_key=True)
    is_host = models.BooleanField(default=False)
    about = models.TextField(max_length=500)
    avatar = models.ImageField('Upload your photo',
                               upload_to=image_dir, null=True)

    def get_absolute_url(self):
        return reverse('accounts:host_profile', args=[self.user.username])