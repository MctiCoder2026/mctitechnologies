from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from core.models import (
    Student, Attendance, Enrollment,
    StaffProfile, StaffAttendance,
)


class Command(BaseCommand):
    help = "Mark missing student and staff attendance absent after 9 PM IST."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        today = timezone.localdate()
        dry_run = options["dry_run"]

        if today.weekday() == 6:
            self.stdout.write(f"{today}: Sunday - skipped")
            return

        students = (
            Student.objects.filter(
                status="active",
                enrollments__status="active",
                enrollments__enrollment_date__lte=today,
            )
            .distinct()
        )

        student_count = 0
        staff_count = 0

        with transaction.atomic():
            for student in students:
                if Attendance.objects.filter(
                    student=student,
                    attendance_date=today,
                ).exists():
                    continue

                enrollment = (
                    Enrollment.objects.filter(
                        student=student,
                        status="active",
                        enrollment_date__lte=today,
                    )
                    .order_by("-enrollment_date", "-id")
                    .first()
                )

                if not enrollment:
                    continue

                student_count += 1

                if not dry_run:
                    Attendance.objects.get_or_create(
                        student=student,
                        attendance_date=today,
                        defaults={
                            "status": "absent",
                            "branch": enrollment.branch or student.branch or "",
                            "course": enrollment.course,
                            "source": "auto",
                            "remarks": "Auto Absent - 9 PM daily scheduler",
                        },
                    )

            staff = StaffProfile.objects.filter(
                is_active=True,
                user__is_active=True,
                joining_date__lte=today,
            )

            for profile in staff:
                if StaffAttendance.objects.filter(
                    staff=profile,
                    attendance_date=today,
                ).exists():
                    continue

                staff_count += 1

                if not dry_run:
                    StaffAttendance.objects.get_or_create(
                        staff=profile,
                        attendance_date=today,
                        defaults={
                            "status": "absent",
                            "branch": profile.branch,
                            "source": "auto_absent",
                        },
                    )

        mode = "DRY RUN" if dry_run else "COMPLETED"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode} | {today} | "
                f"Students: {student_count} | Staff: {staff_count}"
            )
        )
