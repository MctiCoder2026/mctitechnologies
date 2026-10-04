from decimal import Decimal, ROUND_HALF_UP

def calculate_partner_shares(net_amount, partners):
    partners = list(partners)
    if not partners:
        return []
    total = sum(
        (p.share_percentage for p in partners), Decimal("0.00")
    )
    if total != Decimal("100.00"):
        raise ValueError("Active partner percentages must total 100%.")
    net = Decimal(net_amount).quantize(Decimal("0.01"))
    rows = []
    allocated = Decimal("0.00")
    for index, partner in enumerate(partners):
        amount = (
            net - allocated
            if index == len(partners) - 1
            else (net * partner.share_percentage / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )
        allocated += amount
        rows.append({
            "partner": partner,
            "amount": amount,
            "absolute_amount": abs(amount),
            "loss": amount < 0,
        })
    return rows
