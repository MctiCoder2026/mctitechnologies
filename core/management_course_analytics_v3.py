"""MCTI V3 course-wise business intelligence. Read-only."""
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import Lower, Trim

from .models import Admission, Enrollment, FeePayment

ELIGIBLE = ("active", "completed")
ZERO = Decimal("0.00")


def course_business_report(branch=None, course_id=None,
                           start_date=None, end_date=None):
    # Lifetime outstanding is independent of reporting period.
    lifetime_report = None
    if start_date or end_date:
        lifetime_report = course_business_report(
            branch=branch,
            course_id=course_id,
        )

    admissions = Admission.objects.all()
    enrollments = Enrollment.objects.all()
    payments = FeePayment.objects.filter(enrollment__isnull=False)

    if branch and branch != "all":
        key = branch.strip().lower()
        admissions = admissions.annotate(
            branch_key=Lower(Trim("branch"))
        ).filter(branch_key=key)
        enrollments = enrollments.annotate(
            branch_key=Lower(Trim("branch"))
        ).filter(branch_key=key)
        payments = payments.annotate(
            branch_key=Lower(Trim("enrollment__branch"))
        ).filter(branch_key=key)

    if course_id:
        admissions = admissions.filter(course_id=course_id)
        enrollments = enrollments.filter(course_id=course_id)
        payments = payments.filter(enrollment__course_id=course_id)

    if start_date:
        admissions = admissions.filter(admission_date__gte=start_date)
        enrollments = enrollments.filter(enrollment_date__gte=start_date)
        payments = payments.filter(payment_date__gte=start_date)

    if end_date:
        admissions = admissions.filter(admission_date__lte=end_date)
        enrollments = enrollments.filter(enrollment_date__lte=end_date)
        payments = payments.filter(payment_date__lte=end_date)

    admission_counts = {
        row["course_id"]: row["n"]
        for row in admissions.order_by().values("course_id")
        .annotate(n=Count("id"))
    }

    eligible = enrollments.filter(status__in=ELIGIBLE)

    billing_rows = {
        row["course_id"]: row
        for row in eligible.order_by().values(
            "course_id", "course__title"
        ).annotate(
            enrollments=Count("id"),
            billing=Sum("final_fee"),
            discounts=Sum("discount_amount"),
        )
    }

    payment_rows = {
        row["enrollment__course_id"]: row
        for row in payments.order_by().values(
            "enrollment__course_id"
        ).annotate(
            collected=Sum("amount"),
        )
    }

    cancelled_rows = {
        row["enrollment__course_id"]: row["collected"] or ZERO
        for row in payments.filter(
            enrollment__status="cancelled"
        ).order_by().values(
            "enrollment__course_id"
        ).annotate(collected=Sum("amount"))
    }

    from .models import Course
    from django.db.models import OuterRef, Subquery, Value, DecimalField
    from django.db.models.functions import Coalesce

    amount_field = DecimalField(max_digits=14, decimal_places=2)

    payment_subquery = (
        FeePayment.objects.filter(enrollment_id=OuterRef("pk"))
        .order_by().values("enrollment_id")
        .annotate(total=Sum("amount"))
        .values("total")[:1]
    )

    dues = {}
    for item in eligible.annotate(
        paid=Coalesce(
            Subquery(payment_subquery, output_field=amount_field),
            Value(ZERO, output_field=amount_field),
        )
    ).values("course_id", "final_fee", "paid").iterator():
        due = (item["final_fee"] or ZERO) - item["paid"]
        if due > ZERO:
            key = item["course_id"]
            dues[key] = dues.get(key, ZERO) + due

    ids = (
        set(admission_counts)
        | set(billing_rows)
        | set(payment_rows)
        | set(dues)
    )

    titles = dict(Course.objects.filter(
        pk__in=ids
    ).values_list("id", "title"))

    rows = []
    for key in ids:
        billing = billing_rows.get(key, {})
        collected = payment_rows.get(key, {}).get("collected") or ZERO
        cancelled = cancelled_rows.get(key, ZERO)

        rows.append({
            "course_id": key,
            "course": titles.get(key, "Unknown Course"),
            "admissions": admission_counts.get(key, 0),
            "enrollments": billing.get("enrollments", 0),
            "billing": billing.get("billing") or ZERO,
            "discounts": billing.get("discounts") or ZERO,
            "collection": collected,
            "cancelled_collection": cancelled,
            "eligible_collection": collected - cancelled,
            "outstanding": dues.get(key, ZERO),
        })

    rows.sort(key=lambda x: (-x["billing"], x["course"]))

    if lifetime_report is not None:
        lifetime_dues = {
            row["course_id"]: row["outstanding"]
            for row in lifetime_report["rows"]
        }
        for row in rows:
            row["lifetime_outstanding"] = lifetime_dues.get(
                row["course_id"], ZERO
            )
    else:
        for row in rows:
            row["lifetime_outstanding"] = row["outstanding"]

    return {
        "rows": rows,
        "totals": {
            field: sum((row[field] for row in rows), ZERO)
            for field in (
                "billing", "discounts", "collection",
                "cancelled_collection", "eligible_collection",
                "outstanding", "lifetime_outstanding",
            )
        } | {
            "admissions": sum(row["admissions"] for row in rows),
            "enrollments": sum(row["enrollments"] for row in rows),
        },
    }
