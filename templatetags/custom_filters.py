from django import template

register = template.Library()

@register.filter
def get_week_display(value):
    week_map = {
        1: "月",
        2: "火",
        3: "水",
        4: "木",
        5: "金",
        6: "土",
        7: "日",
    }
    return week_map.get(value, "不明")
