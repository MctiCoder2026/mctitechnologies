from django import template
from core.student_basic_details import birthday_context

register = template.Library()

@register.inclusion_tag("core/student_birthday_popup.html", takes_context=True)
def student_birthday_popup(context):
    request = context.get("request")
    if not request:
        return {"birthday_rows": []}
    return birthday_context(request.user)
