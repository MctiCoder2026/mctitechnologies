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
        ("invalid_number", "Invalid Number"),
        ("not_in_service", "Not in Service"),
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


class AlumniMessageActivity(models.Model):
    """Staff-confirmed WhatsApp message history; not delivery verification."""

    MESSAGE_TYPES = [
        ("permission", "Permission Request"),
        ("followup", "Follow-up"),
    ]

    LANGUAGES = [
        ("E", "English"),
        ("M", "Marathi"),
        ("H", "Hindi"),
    ]

    alumni = models.ForeignKey(
        AlumniContact,
        on_delete=models.PROTECT,
        related_name="message_activities",
    )

    staff = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="alumni_message_activities",
    )

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
    )

    language = models.CharField(
        max_length=1,
        choices=LANGUAGES,
    )

    confirmed_at = models.DateTimeField(auto_now_add=True)

    confirmation_token = models.UUIDField(
        unique=True,
        editable=False,
    )

    class Meta:
        ordering = ["-confirmed_at"]
        indexes = [
            models.Index(fields=["alumni", "-confirmed_at"]),
        ]

    def __str__(self):
        return f"{self.alumni_id} - {self.message_type} - {self.staff_id}"
