from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def attr(field, attr_str):
    name, value = attr_str.split(':')
    return field.as_widget(attrs={name: value})