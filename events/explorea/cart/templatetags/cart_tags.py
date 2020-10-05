from django import template

register = template.Library()

@register.simple_tag
def get_key(object, key):
    return object.get(key)