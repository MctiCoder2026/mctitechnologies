from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Admission


class Command(BaseCommand):

    help = (
        "Backfill blank Admission.branch and Student.branch values "
        "from the original Enquiry.branch. Safe by default: dry-run only."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually save changes. Without this flag, only a dry-run report is shown.",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        apply_changes = options["apply"]

        admissions = (
            Admission.objects
            .select_related(
                "enquiry",
                "student",
            )
            .order_by("id")
        )

        total = 0
        admission_fixed = 0
        student_fixed = 0
        already_ok = 0
        unresolved = []
        mismatches = []

        for admission in admissions:

            total += 1

            enquiry = getattr(
                admission,
                "enquiry",
                None
            )

            student = getattr(
                admission,
                "student",
                None
            )

            enquiry_branch = (
                (getattr(enquiry, "branch", None) or "").strip()
                if enquiry
                else ""
            )

            admission_branch = (
                admission.branch or ""
            ).strip()

            student_branch = (
                (getattr(student, "branch", None) or "").strip()
                if student
                else ""
            )

            changed = False

            # ----------------------------------------------------
            # 1. BACKFILL ADMISSION BRANCH FROM ORIGINAL ENQUIRY
            # ----------------------------------------------------

            if not admission_branch and enquiry_branch:

                admission_branch = enquiry_branch

                if apply_changes:

                    admission.branch = enquiry_branch

                    admission.save(
                        update_fields=[
                            "branch",
                        ]
                    )

                admission_fixed += 1
                changed = True

            # ----------------------------------------------------
            # 2. BACKFILL STUDENT BRANCH FROM ADMISSION/ENQUIRY
            # ----------------------------------------------------

            final_branch = (
                admission_branch
                or enquiry_branch
            )

            if (
                student
                and not student_branch
                and final_branch
            ):

                if apply_changes:

                    student.branch = final_branch

                    student.save(
                        update_fields=[
                            "branch",
                        ]
                    )

                student_fixed += 1
                changed = True

            # ----------------------------------------------------
            # 3. REPORT MISMATCHES BUT DO NOT OVERWRITE
            # ----------------------------------------------------

            if (
                enquiry_branch
                and admission_branch
                and enquiry_branch.lower() != admission_branch.lower()
            ):

                mismatches.append(
                    (
                        admission.admission_number,
                        enquiry_branch,
                        admission_branch,
                        student_branch or "-",
                    )
                )

            elif (
                student
                and student_branch
                and final_branch
                and student_branch.lower() != final_branch.lower()
            ):

                mismatches.append(
                    (
                        admission.admission_number,
                        enquiry_branch or "-",
                        admission_branch or "-",
                        student_branch,
                    )
                )

            # ----------------------------------------------------
            # 4. REPORT RECORDS THAT STILL HAVE NO BRANCH SOURCE
            # ----------------------------------------------------

            resolved_student_branch = (
                student_branch
                or final_branch
            )

            if (
                not admission_branch
                and not enquiry_branch
            ):

                unresolved.append(
                    (
                        admission.admission_number,
                        admission.student_name,
                        "No branch in Enquiry or Admission",
                    )
                )

            elif (
                student
                and not resolved_student_branch
            ):

                unresolved.append(
                    (
                        admission.admission_number,
                        admission.student_name,
                        "Student branch could not be resolved",
                    )
                )

            if not changed:

                already_ok += 1

        # Dry-run must never persist anything accidentally.
        if not apply_changes:

            transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write("=" * 60)

        if apply_changes:

            self.stdout.write(
                self.style.SUCCESS(
                    "BRANCH BACKFILL APPLIED"
                )
            )

        else:

            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN ONLY - DATABASE NOT CHANGED"
                )
            )

        self.stdout.write("=" * 60)

        self.stdout.write(
            f"Total admissions checked : {total}"
        )

        self.stdout.write(
            f"Admission branches to fix: {admission_fixed}"
        )

        self.stdout.write(
            f"Student branches to fix  : {student_fixed}"
        )

        self.stdout.write(
            f"Already OK / unchanged   : {already_ok}"
        )

        self.stdout.write(
            f"Unresolved records       : {len(unresolved)}"
        )

        self.stdout.write(
            f"Branch mismatches         : {len(mismatches)}"
        )

        if unresolved:

            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "UNRESOLVED:"
                )
            )

            for admission_no, name, reason in unresolved:

                self.stdout.write(
                    f"  {admission_no} | {name} | {reason}"
                )

        if mismatches:

            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "MISMATCHES - NOT OVERWRITTEN:"
                )
            )

            for admission_no, enquiry_b, admission_b, student_b in mismatches:

                self.stdout.write(
                    f"  {admission_no} | "
                    f"Enquiry={enquiry_b} | "
                    f"Admission={admission_b} | "
                    f"Student={student_b}"
                )

        self.stdout.write("")
        self.stdout.write("=" * 60)

        if not apply_changes:

            self.stdout.write(
                "If this report looks correct, run again with --apply"
            )

        else:

            self.stdout.write(
                self.style.SUCCESS(
                    "Backfill completed successfully."
                )
            )
