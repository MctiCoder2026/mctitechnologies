from decimal import Decimal

from django.db import migrations


PARTNERS = [
    (
        "kharghar",
        "Sunil",
        Decimal("100.00"),
    ),
    (
        "nerul",
        "Sunil B.",
        Decimal("33.34"),
    ),
    (
        "nerul",
        "Bhagyashri W.",
        Decimal("33.33"),
    ),
    (
        "nerul",
        "Prasad B.",
        Decimal("33.33"),
    ),
]


def create_initial_partners(
    apps,
    schema_editor
):

    BranchPartner = apps.get_model(
        "core",
        "BranchPartner"
    )

    for (
        branch,
        partner_name,
        share_percentage
    ) in PARTNERS:

        BranchPartner.objects.update_or_create(
            branch=branch,
            partner_name=partner_name,
            defaults={
                "share_percentage": (
                    share_percentage
                ),
                "is_active": True,
            }
        )


def keep_partner_records(
    apps,
    schema_editor
):
    # Financial master data is intentionally
    # preserved if migration is reversed.
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0038_monthlybranchclosing_reserve_fund_amount",
        ),
    ]

    operations = [
        migrations.RunPython(
            create_initial_partners,
            keep_partner_records,
        ),
    ]