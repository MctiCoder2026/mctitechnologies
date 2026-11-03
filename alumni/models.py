from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class AlumniContact(models.Model):

    BRANCH_CHOICES = [
        ("kharghar", "Kharghar"),
        ("panvel", "Panvel"),
        ("koperkhairane", "Koperkhairane"),
    ]

    STATUS_CHOICES = [
        ("new", "Not Contacted"),
        ("contacted", "Contacted"),
        ("interested", "Interested"),
        ("followup", "Follow Up"),
        ("converted", "Converted"),
        ("not_interested", "Not Interested"),
        ("do_not_contact", "Do Not Contact"),
    ]

    PERMISSION_CHOICES = [
        ("unknown", "Unknown"),
        ("allowed", "Allowed"),
        ("declined", "Declined"),
    ]

    name = models.CharField(max_length=150)

    mobile = models.CharField(max_length=20, db_index=True)

    normalized_mobile = models.CharField(
        max_length=15,
        blank=True,
        db_index=True,
    )

    email = models.EmailField(blank=True)

    branch = models.CharField(
        max_length=30,
        choices=BRANCH_CHOICES,
        db_index=True,
    )

    admission_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(2013),
            MaxValueValidator(2025),
        ],
    )

    previous_course = models.CharField(
        max_length=200,
        blank=True,
    )

    source_file = models.CharField(
        max_length=255,
        blank=True,
    )

    permission_status = models.CharField(
        max_length=20,
        choices=PERMISSION_CHOICES,
        default="unknown",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="new",
        db_index=True,
    )

    followup_date = models.DateField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(blank=True)

    last_contacted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["branch", "admission_year"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.branch}"
