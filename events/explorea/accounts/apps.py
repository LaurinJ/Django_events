from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save

class AccountsConfig(AppConfig):
    name = 'explorea.accounts'

    def ready(self):
        import explorea.accounts.signals as signals

        post_save.connect(signals.create_profile, sender=settings.AUTH_USER_MODEL)
