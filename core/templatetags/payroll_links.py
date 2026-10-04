from django import template
from core.employee_payroll import manager_access
register = template.Library()

@register.inclusion_tag("core/payroll_links.html", takes_context=True)
def payroll_links(context):
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return {}
    user = request.user
    staff = getattr(user, "staff_profile", None)
    trainer = getattr(user, "classroom_trainer_profile", None)
    return {
        "payroll_manager": manager_access(user),
        "payroll_employee": user.is_active and (
            bool(staff and staff.is_active) or bool(trainer and trainer.is_active)
        ),
    }
