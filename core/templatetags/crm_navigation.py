from django import template
from core.views import is_admin_user, can_view_business_amounts

register = template.Library()

@register.inclusion_tag("core/crm_sidebar.html", takes_context=True)
def crm_sidebar(context):
    request = context.get("request")
    if not request:
        return {}
    user = request.user
    resolver = getattr(request, "resolver_match", None)
    profile = getattr(user, "staff_profile", None)
    trainer = getattr(user, "classroom_trainer_profile", None)
    employee_access = bool(
        user.is_authenticated and user.is_active and (
            (profile and profile.is_active)
            or (trainer and trainer.is_active)
        )
    )
    return {
        "request": request,
        "nav_current": resolver.view_name if resolver else "",
        "nav_admin": is_admin_user(user),
        "nav_power": bool(user.is_authenticated and user.is_active
                          and user.is_superuser),
        "nav_financial": can_view_business_amounts(user),
        "nav_employee": employee_access,
        "nav_outreach": context.get("can_access_outreach", False),
    }
