from django import template
from urllib.parse import urlencode, parse_qsl

register = template.Library()

@register.filter
def remove_get_param(querystring, param):
    """
    Usuwa parametr GET z querystringa
    """
    query_dict = dict(parse_qsl(querystring))
    query_dict.pop(param, None)
    return urlencode(query_dict, doseq=True)