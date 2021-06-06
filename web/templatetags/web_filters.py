from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='dict_filter')
def dict_filter(dictionary, key):
    return dictionary[key]

@register.filter(name='unique_keys')
def unique_keys(list_obj, key):
     output = list(set([item[key] for item in list_obj]))
     output.sort()
     return output