from django import template

register = template.Library()


@register.filter
def level_to_text(level):
    level_mapping = {1: "풋린이", 2: "풋내기", 3: "풋아마", 4: "풋현역", 5: "풋롱도르"}
    return level_mapping.get(level, "Unknown")
