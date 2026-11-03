"""
MCTI Management Command Center V3.

Read-only analytics service.
No database writes or schema changes.
"""

from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import Lower, Trim
from django.utils import timezone

from .models import Admission, Enquiry, Enrollment, FeePayment


BRANCHES = (
    ("kharghar", "Kharghar"),
    ("panvel", "Panvel"),
    ("koperkhairane", "Koperkhairane"),
    ("kamothe", "Kamothe"),
    ("ghansoli", "Ghansoli"),
    ("nerul", "Nerul"),
)

ELIGIBLE_ENROLLMENT_STATUSES = ("active", "completed")


def money(value):
    return value if value is not None else Decimal("0.00")


def eligible_enquiries():
    return Enquiry.objects.exclude(
        message__icontains="MCTI AI Ready Maharashtra"
    )


def normalized_branches(queryset):
    return queryset.annotate(
        normalized_branch=Lower(Trim("branch"))
    )


def branch_performance(start_date=None, end_date=None):
    """
    Date filters apply to each metric's own event date.
    Outstanding is deliberately not calculated here.
    """
    enquiries = normalized_branches(eligible_enquiries())
    admissions = normalized_branches(Admission.objects.all())
    enrollments = normalized_branches(Enrollment.objects.all())

    payments = FeePayment.objects.filter(
        enrollment__isnull=False
    ).annotate(
        normalized_branch=Lower(Trim("enrollment__branch"))
    )

    if start_date:
        enquiries = enquiries.filter(
            created_at__date__gte=start_date
        )
        admissions = admissions.filter(
            admission_date__gte=start_date
        )
        enrollments = enrollments.filter(
            enrollment_date__gte=start_date
        )
        payments = payments.filter(
            payment_date__gte=start_date
        )

    if end_date:
        enquiries = enquiries.filter(
            created_at__date__lte=end_date
        )
        admissions = admissions.filter(
            admission_date__lte=end_date
        )
        enrollments = enrollments.filter(
            enrollment_date__lte=end_date
        )
        payments = payments.filter(
            payment_date__lte=end_date
        )

    rows = []

    for key, label in BRANCHES:
        eq = enquiries.filter(normalized_branch=key)
        ad = admissions.filter(normalized_branch=key)
        en = enrollments.filter(normalized_branch=key)
        pay = payments.filter(normalized_branch=key)

        collection = money(
            pay.aggregate(total=Sum("amount"))["total"]
        )

        cancelled_collection = money(
            pay.filter(
                enrollment__status="cancelled"
            ).aggregate(total=Sum("amount"))["total"]
        )

        eligible_fees = money(
            en.filter(
                status__in=ELIGIBLE_ENROLLMENT_STATUSES
            ).aggregate(total=Sum("final_fee"))["total"]
        )

        rows.append({
            "key": key,
            "branch": label,
            "enquiries": eq.count(),
            "admissions": ad.count(),
            "enrollments": en.count(),
            "eligible_fees": eligible_fees,
            "collection": collection,
            "cancelled_collection": cancelled_collection,
        })

    return rows



def outstanding_by_branch():
    """
    Lifetime outstanding for active/completed enrollments.

    Payments are matched to each enrollment individually.
    Cancelled enrollments are excluded.
    Overpayments cannot offset another enrollment's balance.
    """
    from django.db.models import OuterRef, Subquery, Value
    from django.db.models.functions import Coalesce
    from django.db.models import DecimalField

    payment_total = (
        FeePayment.objects.filter(
            enrollment_id=OuterRef("pk")
        )
        .values("enrollment_id")
        .annotate(total=Sum("amount"))
        .values("total")[:1]
    )

    enrollments = (
        Enrollment.objects.filter(
            status__in=ELIGIBLE_ENROLLMENT_STATUSES
        )
        .annotate(
            normalized_branch=Lower(Trim("branch")),
            paid_total=Coalesce(
                Subquery(
                    payment_total,
                    output_field=DecimalField(
                        max_digits=14,
                        decimal_places=2
                    )
                ),
                Value(
                    Decimal("0.00"),
                    output_field=DecimalField(
                        max_digits=14,
                        decimal_places=2
                    )
                )
            )
        )
        .values(
            "normalized_branch",
            "final_fee",
            "paid_total"
        )
    )

    totals = {
        key: Decimal("0.00")
        for key, _ in BRANCHES
    }

    for item in enrollments.iterator():
        branch = item["normalized_branch"]

        if branch not in totals:
            continue

        due = money(item["final_fee"]) - money(item["paid_total"])

        if due > 0:
            totals[branch] += due

    return totals



def crm_conversion_by_branch(start_date=None, end_date=None):
    """
    Enquiry-cohort conversion analytics.

    Date filters select enquiries by their creation date.
    Admission-linked conversion uses Admission.enquiry_id.
    """
    enquiries = normalized_branches(eligible_enquiries())

    if start_date:
        enquiries = enquiries.filter(
            created_at__date__gte=start_date
        )

    if end_date:
        enquiries = enquiries.filter(
            created_at__date__lte=end_date
        )

    results = []

    for key, label in BRANCHES:
        branch_enquiries = enquiries.filter(
            normalized_branch=key
        )

        total = branch_enquiries.count()

        status_converted = branch_enquiries.filter(
            status="converted"
        ).count()

        admission_linked = Admission.objects.filter(
            enquiry_id__in=branch_enquiries.values("id")
        ).count()

        results.append({
            "key": key,
            "branch": label,
            "total_enquiries": total,
            "status_converted": status_converted,
            "admission_linked": admission_linked,
            "status_conversion_rate": round(
                status_converted * 100 / total, 2
            ) if total else 0.0,
            "verified_conversion_rate": round(
                admission_linked * 100 / total, 2
            ) if total else 0.0,
        })

    return results



# MCTI_V3_CANCELLATION_ANALYTICS_V1
def cancellation_loss_by_branch():
    """Lifetime cancelled enrollment values, grouped by home branch.

    Potential loss is unpaid cancelled fee value, not accounting loss.
    Payments are matched individually to avoid cross-enrollment offsets.
    """
    from django.db.models import Sum

    payments = dict(
        FeePayment.objects.filter(
            enrollment__status="cancelled"
        )
        .values("enrollment_id")
        .annotate(total=Sum("amount"))
        .values_list("enrollment_id", "total")
    )

    totals = {
        key: {
            "cancelled_count": 0,
            "cancelled_fee": Decimal("0.00"),
            "cancelled_received": Decimal("0.00"),
            "potential_loss": Decimal("0.00"),
        }
        for key, _ in BRANCHES
    }

    enrollments = (
        Enrollment.objects.filter(status="cancelled")
        .annotate(normalized_branch=Lower(Trim("branch")))
        .values("id", "normalized_branch", "final_fee")
    )

    for enrollment in enrollments.iterator():
        key = enrollment["normalized_branch"]

        if key not in totals:
            continue

        fee = money(enrollment["final_fee"])
        received = money(payments.get(enrollment["id"]))

        row = totals[key]
        row["cancelled_count"] += 1
        row["cancelled_fee"] += fee
        row["cancelled_received"] += received
        row["potential_loss"] += max(
            fee - received, Decimal("0.00")
        )

    return totals


def executive_summary(start_date=None, end_date=None):
    rows = branch_performance(start_date, end_date)
    outstanding = outstanding_by_branch()
    cancellation = cancellation_loss_by_branch()
    crm_rows = crm_conversion_by_branch(start_date, end_date)
    crm_by_key = {item["key"]: item for item in crm_rows}

    for row in rows:
        row["crm_conversion"] = crm_by_key[row["key"]]

    crm_total_enquiries = sum(
        item["total_enquiries"] for item in crm_rows
    )
    crm_status_converted = sum(
        item["status_converted"] for item in crm_rows
    )
    crm_admission_linked = sum(
        item["admission_linked"] for item in crm_rows
    )

    for row in rows:
        row["outstanding"] = outstanding.get(
            row["key"], Decimal("0.00")
        )
        row.update(cancellation[row["key"]])

    return {
        "branches": rows,
        "crm_conversion": crm_rows,
        "total_status_converted": crm_status_converted,
        "total_admission_linked": crm_admission_linked,
        "status_conversion_rate": round(
            crm_status_converted * 100 / crm_total_enquiries, 2
        ) if crm_total_enquiries else 0.0,
        "verified_conversion_rate": round(
            crm_admission_linked * 100 / crm_total_enquiries, 2
        ) if crm_total_enquiries else 0.0,
        "total_outstanding": sum(
            outstanding.values(), Decimal("0.00")
        ),
        "total_enquiries": sum(
            row["enquiries"] for row in rows
        ),
        "total_admissions": sum(
            row["admissions"] for row in rows
        ),
        "total_collection": sum(
            (row["collection"] for row in rows),
            Decimal("0.00"),
        ),
        "cancelled_collection": sum(
            (row["cancelled_collection"] for row in rows),
            Decimal("0.00"),
        ),
        "total_cancelled_count": sum(
            row["cancelled_count"] for row in rows
        ),
        "total_cancelled_fee": sum(
            (row["cancelled_fee"] for row in rows),
            Decimal("0.00"),
        ),
        "total_cancelled_received": sum(
            (row["cancelled_received"] for row in rows),
            Decimal("0.00"),
        ),
        "total_potential_loss": sum(
            (row["potential_loss"] for row in rows),
            Decimal("0.00"),
        ),
        "generated_at": timezone.now(),
    }
