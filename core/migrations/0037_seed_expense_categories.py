from django.db import migrations


EXPENSE_CATEGORIES = [
    (
        "Office Rent",
        "office_rent",
        1,
    ),
    (
        "Staff Salary",
        "staff_salary",
        2,
    ),
    (
        "Electricity / Light Bill",
        "electricity",
        3,
    ),
    (
        "Government Fee",
        "government_fee",
        4,
    ),
    (
        "Computer Maintenance",
        "computer_maintenance",
        5,
    ),
    (
        "Internet Bill",
        "internet",
        6,
    ),
    (
        "Mobile Recharge",
        "mobile_recharge",
        7,
    ),
    (
        "Advertisement / Marketing",
        "advertisement",
        8,
    ),
    (
        "Stationery",
        "stationery",
        9,
    ),
    (
        "Housekeeping / Cleaning",
        "housekeeping",
        10,
    ),
    (
        "Travelling / Conveyance",
        "travelling",
        11,
    ),
    (
        "Repairs and Maintenance",
        "repairs_maintenance",
        12,
    ),
    (
        "Refreshment",
        "refreshment",
        13,
    ),
    (
        "Professional / Consultancy Fee",
        "professional_fee",
        14,
    ),
    (
        "Miscellaneous",
        "miscellaneous",
        15,
    ),
    (
        "Other Expense",
        "other",
        16,
    ),
]


def create_expense_categories(
    apps,
    schema_editor
):

    ExpenseCategory = apps.get_model(
        "core",
        "ExpenseCategory"
    )

    for name, code, order in EXPENSE_CATEGORIES:

        ExpenseCategory.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "display_order": order,
                "is_active": True,
            }
        )


def keep_expense_categories(
    apps,
    schema_editor
):
    # Do not delete financial master data
    # if this migration is reversed.
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0036_expensecategory_dailybranchexpense_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            create_expense_categories,
            keep_expense_categories,
        ),
    ]