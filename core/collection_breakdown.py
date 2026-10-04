from decimal import Decimal
from urllib.parse import urlencode

from django.db.models import Q, Sum
from django.urls import reverse
from .models import Enrollment, FeePayment


def branch_payments(branch):
    return FeePayment.objects.filter(
        Q(enrollment__branch__iexact=branch)
        | Q(enrollment__isnull=True, student__branch__iexact=branch)
    )


def collection_groups(branch, start=None, end=None):
    valid = Enrollment.objects.filter(
        branch__iexact=branch
    ).exclude(status="cancelled")
    fresh = valid
    if start and end:
        fresh = fresh.filter(enrollment_date__range=(start, end))
        old = valid.filter(enrollment_date__lt=start)
    else:
        old = valid.none()

    payments = branch_payments(branch)
    if start and end:
        payments = payments.filter(payment_date__range=(start, end))

    fresh_q = Q(enrollment_id__in=fresh.values("pk"))
    old_q = Q(enrollment_id__in=old.values("pk"))
    return fresh, {
        "total": payments,
        "fresh": payments.filter(fresh_q),
        "old": payments.filter(old_q),
        "other": payments.exclude(fresh_q | old_q),
    }


def breakdown(branch, start=None, end=None):
    fresh, groups = collection_groups(branch, start, end)
    values = {
        key: qs.aggregate(value=Sum("amount"))["value"] or Decimal("0")
        for key, qs in groups.items()
    }
    assert values["total"] == values["fresh"] + values["old"] + values["other"]

    paid = FeePayment.objects.filter(
        enrollment_id__in=fresh.values("pk")
    )
    if end:
        paid = paid.filter(payment_date__lte=end)
    paid_map = {
        row["enrollment_id"]: row["value"]
        for row in paid.values("enrollment_id").annotate(value=Sum("amount"))
    }
    pending = sum(
        (max(fee - paid_map.get(pk, Decimal("0")), Decimal("0"))
         for pk, fee in fresh.values_list("pk", "final_fee")),
        Decimal("0"),
    )
    params = {"branch": branch}
    if start and end:
        params.update(start_date=start.isoformat(), end_date=end.isoformat())
    links = {
        key: reverse("fee_payment_list") + "?" + urlencode(
            dict(params, collection_type=key)
        ) for key in groups
    }
    return {
        "collection": values["total"],
        "fresh_collection": values["fresh"],
        "old_collection": values["old"],
        "other_collection": values["other"],
        "outstanding": pending,
        "collection_url": links["total"],
        "fresh_collection_url": links["fresh"],
        "old_collection_url": links["old"],
        "other_collection_url": links["other"],
    }
