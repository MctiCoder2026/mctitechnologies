from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Student, Attendance, Enrollment


class Command(BaseCommand):

    help = "Automatically mark absent for eligible active students without attendance."

    def handle(self, *args, **options):

        today = timezone.localdate()

        # Sunday weekly off
        if today.weekday() == 6:
            self.stdout.write(
                self.style.WARNING(
                    f"{today}: Sunday - Auto Absent skipped."
                )
            )
            return

        # Students having at least one active enrollment
        students = (
            Student.objects
            .filter(
                status="active",
                enrollments__status="active",
                enrollments__enrollment_date__lte=today,
            )
            .distinct()
            .select_related("course")
        )

        created_count = 0
        skipped_count = 0

        for student in students:

            exists = Attendance.objects.filter(
                student=student,
                attendance_date=today,
            ).exists()

            if exists:
                skipped_count += 1
                continue

            # Pick student's latest active enrollment for course/branch snapshot
            enrollment = (
                Enrollment.objects
                .filter(
                    student=student,
                    status="active",
                    enrollment_date__lte=today,
                )
                .order_by("-enrollment_date", "-id")
                .first()
            )

            Attendance.objects.create(
                student=student,
                attendance_date=today,
                status="absent",
                branch=(
                    enrollment.branch
                    if enrollment and enrollment.branch
                    else student.branch or ""
                ),
                course=(
                    enrollment.course
                    if enrollment
                    else student.course
                ),
                first_login_time=None,
                latitude=None,
                longitude=None,
                source="auto",
                marked_by=None,
                remarks="Auto Absent - No attendance marked by day end",
            )

            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Auto Absent completed for {today}. "
                f"Absent created: {created_count}, "
                f"Skipped: {skipped_count}"
            )
        )