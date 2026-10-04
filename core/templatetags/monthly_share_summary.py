from django import template
from core.monthly_share_calculation import calculate_partner_shares

register = template.Library()

@register.inclusion_tag("core/monthly_share_summary.html")
def monthly_share_summary(closing, partners):
    enabled = closing.status in ("draft", "submitted")
    rows, error = [], ""
    if enabled:
        try:
            rows = calculate_partner_shares(
                closing.cash_profit - closing.reserve_fund_amount, list(partners.order_by("pk"))
            )
        except ValueError as exc:
            error = str(exc)
    return {
        "closing": closing,
        "preview_enabled": enabled,
        "share_rows": rows,
        "share_error": error,
        "net_absolute": abs(closing.cash_profit),
        "after_reserve": closing.cash_profit - closing.reserve_fund_amount,
    }
