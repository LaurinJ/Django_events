from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def min_attr_value(objects, field_name):
    values = [getattr(obj,field_name) for obj in objects]
    if values:
        return min(values)

@register.filter
def next_date(objects,field_name="date"):
    dates = sorted(objects.values_list(field_name, flat=True))
    for dt in dates:
        if dt >= timezone.now().date():
            return dt

@register.filter
def active(objects, date_field="date"):
    return [obj for obj in objects if getattr(obj,date_field) >= timezone.now().date()]

@register.filter
def has(obj, attr_name):
    try:
        return bool(getattr(obj, attr_name))
    except ValueError:
        return False