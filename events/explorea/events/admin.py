from django.contrib import admin
from .models import Event, EventRun
from django.db.models import Count, Q
from django.utils import timezone
import csv
from django.http import HttpResponse
from django.urls import path
from django import forms
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from io import StringIO
from django.contrib import messages
from django.utils.html import format_html

UserModel = get_user_model()

def export_to_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta

    # get table header
    field_names = [field.name for field in meta.fields]
    filename = '{}_Events'.format(timezone.now().strftime('%Y_%m_%d'))
    # create response object to be sent
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
    # csv writer object that needs the response to write in
    writer = csv.writer(response)

    # write the data
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow(getattr(obj, field) for field in field_names)
    return response

class EventRunInline(admin.TabularInline):
    model = EventRun

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    change_list_template = "admin/events_changelist.html"

    list_display = ['host',
                    'name',
                    'category',
                    'slug',
                    'truncate_description',
                    'location',
                    'events_passed',
                    'events_active',
                    'truncate_description',
                    'created',
                    'thumbnail',
                    'main_image',
                    ]

    inlines = [EventRunInline]
    actions = [export_to_csv]
    list_filter = ['category', 'created']
    date_hierarchy = 'created'
    search_fields = ['host__username', 'name', 'location']
    list_editable = ['name', 'category', 'location']
    readonly_fields = ['thumbnail_image', 'main_image_picture']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            events_passed=Count('eventrun', filter=Q(eventrun__date__lt=timezone.now())),
            events_future=Count('eventrun', filter=Q(eventrun__date__gte=timezone.now()))
        )
        return qs


    def events_passed(self, obj):
        return obj.events_passed

    events_passed.admin_order_field = 'events_passed'

    def events_active(self, obj):
        return obj.events_future
    events_active.admin_order_field = 'events_future'

    def truncate_description(self, obj):
        length = 40
        if len(obj.description) > length:
            return obj.description[:length] + '...'
        elif len(obj.description) > 0:
            return obj.description + '...'
        else:
            return '-----------'
    truncate_description.short_description = "Description"

    def get_urls(self):
        import_url = [path('import_csv/', self.import_csv, name='import_csv')]
        return import_url + super().get_urls()

    def thumbnail_image(self, obj):
        return format_html('<img src={}>', obj.thumbnail.url)

    def main_image_picture(self, obj):
        return format_html('<img src={}>', obj.main_image.url)

    def import_csv(self, request):
        if request.method == 'POST':

            form = CSVImportForm(files=request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                data_stream = StringIO()
                for chunk in file.chunks():
                    data_stream.write(chunk.decode())

                try:
                    data_stream.seek(0)
                    reader = csv.DictReader(data_stream)
                    for index, line in enumerate(reader):
                        line['host'] = UserModel.objects.get(pk=int(line['host']))
                        Event.objects.update_or_create(**line)
                    self.message_user(request, "The file {} has been imported".format(file.name))

                except Exception as e:
                    messages.error(request,
                                   ("The file {} could not be imported. "
                                    "Problem on line {}. "
                                    "(HINT: {})").format(file.name, index + 2, e.args[0]))
                finally:
                    data_stream.close()
                return redirect(reverse('admin:events_event_changelist'))
        form = CSVImportForm()
        return render(request, 'admin/csv_import.html', {'form': form})

class CSVImportForm(forms.Form):
    file = forms.FileField()

