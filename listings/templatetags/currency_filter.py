from django import template
import locale
from django.template.defaultfilters import stringfilter

register=template.Library()

@register.filter
@stringfilter
# creating custom currency filter
def format_currency(amount):
    locale.setlocale(locale.LC_ALL,locale="en_IN")
    return locale.currency(int(amount),symbol=True,grouping=True).replace(".00","")