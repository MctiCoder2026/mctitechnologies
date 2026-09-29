from django.db import models
from core.models import BranchLocation


class SSCStudent(models.Model):

    MEDIUM_CHOICES = [
        ("english", "English"),
        ("marathi", "Marathi"),
        ("semi_english", "Semi-English"),
    ]

    full_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, db_index=True)
    school_name = models.CharField(max_length=200)
    medium = models.CharField(max_length=20, choices=MEDIUM_CHOICES)
    city = models.CharField(max_length=100, blank=True)

    preferred_branch = models.ForeignKey(
        BranchLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ssc_exam_students",
    )

    consent_given = models.BooleanField(default=False)

    enquiry = models.ForeignKey(
        "core.Enquiry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ssc_exam_leads",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.mobile}"


class SSCResource(models.Model):

    SUBJECT_CHOICES = [
        ("maths_1", "Mathematics Part 1"),
        ("maths_2", "Mathematics Part 2"),
        ("science_1", "Science & Technology Part 1"),
        ("science_2", "Science & Technology Part 2"),
        ("english", "English"),
        ("marathi", "Marathi"),
        ("history", "History & Political Science"),
        ("geography", "Geography"),
    ]

    RESOURCE_TYPES = [
        ("previous_paper", "Previous Year Question Paper"),
        ("sample_paper", "Sample Paper"),
        ("practice", "MCTI Practice Material"),
    ]

    title = models.CharField(max_length=250)
    subject = models.CharField(max_length=30, choices=SUBJECT_CHOICES)
    year = models.PositiveIntegerField(null=True, blank=True)

    resource_type = models.CharField(
        max_length=30,
        choices=RESOURCE_TYPES,
        default="previous_paper",
    )

    medium = models.CharField(
        max_length=20,
        choices=SSCStudent.MEDIUM_CHOICES,
        default="english",
    )

    source_name = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(max_length=1000, blank=True)

    file = models.FileField(
        upload_to="ssc_exam_resources/",
        blank=True,
        null=True,
    )

    is_official_source = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "subject", "title"]

    def __str__(self):
        return self.title


class SSCDownload(models.Model):

    student = models.ForeignKey(
        SSCStudent,
        on_delete=models.CASCADE,
        related_name="downloads",
    )

    resource = models.ForeignKey(
        SSCResource,
        on_delete=models.CASCADE,
        related_name="downloads",
    )

    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-downloaded_at"]

    def __str__(self):
        return f"{self.student} → {self.resource}"
