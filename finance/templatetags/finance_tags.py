import math
from django import template

register = template.Library()

@register.filter(name='floor_number')
def floor_number(value):
    try:
        if value is None:
            return 0
        return math.floor(float(value))
    except (TypeError, ValueError):
        return value
