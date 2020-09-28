from django.contrib import admin
from .models import Profile

admin.site.site_header = 'Explorea Admin'
admin.site.site_title = 'Explorea Admin'
admin.site.index_title = 'Select the model ...'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass