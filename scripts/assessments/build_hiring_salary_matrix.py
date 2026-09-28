from assessments.models import HiringJobRole, HiringSalaryMatrix

# MCTI monthly salary guidance.
# Format: employment_type -> performance_band -> (min_salary, max_salary)
#
# Change amounts here before running the script.
SALARY_POLICY = {
    "intern": {
        "not_shortlisted": (0, 0),
        "trainee": (5000, 7000),
        "junior": (7000, 9000),
        "skilled": (9000, 12000),
        "advanced": (12000, 15000),
    },

    "part_time": {
        "not_shortlisted": (0, 0),
        "trainee": (7000, 10000),
        "junior": (10000, 13000),
        "skilled": (13000, 17000),
        "advanced": (17000, 22000),
    },

    "full_time": {
        "not_shortlisted": (0, 0),
        "trainee": (10000, 14000),
        "junior": (14000, 18000),
        "skilled": (18000, 25000),
        "advanced": (25000, 35000),
    },

    "trainer": {
        "not_shortlisted": (0, 0),
        "trainee": (10000, 15000),
        "junior": (15000, 20000),
        "skilled": (20000, 28000),
        "advanced": (28000, 40000),
    },
}


def run():
    roles = HiringJobRole.objects.filter(is_active=True).order_by("name")

    created = 0
    updated = 0

    for role in roles:
        for employment_type, bands in SALARY_POLICY.items():
            for performance_band, salary_range in bands.items():

                min_salary, max_salary = salary_range

                obj, was_created = HiringSalaryMatrix.objects.update_or_create(
                    job_role=role,
                    employment_type=employment_type,
                    performance_band=performance_band,
                    defaults={
                        "min_salary": min_salary,
                        "max_salary": max_salary,
                        "is_active": True,
                    },
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

    print("=" * 60)
    print("MCTI HIRING SALARY MATRIX")
    print("=" * 60)
    print("Active Roles:", roles.count())
    print("Created:", created)
    print("Updated:", updated)
    print("Total Matrix Records:", HiringSalaryMatrix.objects.count())
    print("=" * 60)


if __name__ == "__main__":
    run()
