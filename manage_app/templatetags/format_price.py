from django import template

register = template.Library()

@register.filter('format_price')
def format_price(price):
    return f"{price:,}".replace(",", ".")