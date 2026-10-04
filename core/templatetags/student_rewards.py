from django import template
from django.db.models import Sum
from core.models import Student, StudentRewardEntry

register = template.Library()

@register.inclusion_tag("core/student_reward_wallet.html", takes_context=True)
def student_reward_wallet(context):
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return {"reward_wallet_visible": False}
    student = Student.objects.filter(user_id=request.user.pk).first()
    if student is None:
        return {"reward_wallet_visible": False}
    entries = StudentRewardEntry.objects.filter(student=student)
    earned = entries.filter(points__gt=0).aggregate(
        value=Sum("points")
    )["value"] or 0
    used = -(entries.filter(points__lt=0).aggregate(
        value=Sum("points")
    )["value"] or 0)
    return {
        "reward_wallet_visible": True,
        "wallet_balance": earned-used,
        "wallet_earned": earned,
        "wallet_used": used,
        "wallet_entries": list(entries[:10]),
    }
