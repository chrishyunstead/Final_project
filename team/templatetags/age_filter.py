import datetime
from django import template

register = template.Library()


@register.filter
def age(birth_date):
    if birth_date:
        today = datetime.date.today()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (
            today.month == birth_date.month and today.day < birth_date.day
        ):
            age -= 1
        return f"{age}세"
    return ""
