import re
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def next_page(context, page_num):
    request = context.get('request')
    path = request.get_full_path()
    regex = re.compile(r'page=\d*\&?')
    URL = regex.sub('', path).rstrip('&')

    if '?' not in URL:
        URL += '?'
    else:
        URL += '&'
    URL += 'page={}'.format(page_num)
    return URL