from django import template
register = template.Library()
@register.filter
def has(obj, attr_name):
    try:
        return bool(getattr(obj, attr_name))
    except ValueError:
        return False