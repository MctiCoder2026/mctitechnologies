
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# ============================================================
# COURSE
# ============================================================

class Course(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )

    short_description = models.TextField()

    syllabus = models.TextField(
        blank=True,
        null=True
    )

    eligibility = models.TextField(
        blank=True,
        null=True
    )

    benefits = models.TextField(
        blank=True,
        null=True
    )

    duration = models.CharField(
        max_length=100
    )

    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    category = models.CharField(
        max_length=100
    )

    icon = models.CharField(
        max_length=10,
        default="📚"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.slug:

            from django.utils.text import slugify

            self.slug = slugify(
                self.title
            )

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return self.title


# ============================================================
# COURSE MODULE
# ============================================================

class CourseModule(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules"
    )

    module_number = models.PositiveIntegerField()

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):

        return (
            f"{self.course.title} "
            f"- Module {self.module_number}"
        )

    class Meta:

        ordering = [
            "module_number"
        ]


# ============================================================
# ENQUIRY / LEAD
# ============================================================

class Enquiry(models.Model):

    STATUS_CHOICES = [

        ("new", "New"),

        ("contacted", "Contacted"),

        ("followup", "Follow Up"),

        ("converted", "Converted"),

        ("closed", "Closed"),

    ]

    name = models.CharField(
        max_length=100
    )

    mobile = models.CharField(
        max_length=15
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    branch = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    message = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )

    followup_date = models.DateField(
        null=True,
        blank=True
    )

    followup_notes = models.TextField(
        blank=True,
        null=True
    )

    # OLD ASSIGNMENT FIELD
    assigned_to = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # NEW STAFF ASSIGNMENT
    assigned_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_enquiries"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.name} - {self.mobile}"
        )

    class Meta:

        ordering = [
            "-created_at"
        ]


# ============================================================
# ENQUIRY ACTIVITY
# ============================================================

class EnquiryActivity(models.Model):

    ACTIVITY_TYPES = [

        ("call", "Call"),

        ("whatsapp", "WhatsApp"),

        ("note", "Note"),

        ("status", "Status Changed"),

        ("followup", "Follow-up"),

        ("converted", "Converted"),

    ]

    enquiry = models.ForeignKey(
        Enquiry,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enquiry_activities"
    )

    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPES
    )

    message = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return (
            f"{self.enquiry.name} - "
            f"{self.get_activity_type_display()}"
        )


# ============================================================
# ADMISSION
# ============================================================
class Admission(models.Model):

    PAYMENT_STATUS_CHOICES = [

        ("pending", "Pending"),
        ("partial", "Partially Paid"),
        ("paid", "Fully Paid"),

    ]

    PAYMENT_MODE_CHOICES = [

        ("cash", "Cash"),
        ("upi", "UPI"),
        ("bank", "Bank Transfer"),
        ("card", "Card"),
        ("cheque", "Cheque"),

    ]

    # --------------------------------------------------------
    # ADMISSION NUMBER
    # --------------------------------------------------------

    admission_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    # --------------------------------------------------------
    # LINK WITH LEAD
    # --------------------------------------------------------

    enquiry = models.OneToOneField(
        Enquiry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admission"
    )

    # --------------------------------------------------------
    # LOGIN USER
    # --------------------------------------------------------

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="student_profile"
    )

    # --------------------------------------------------------
    # STUDENT INFORMATION
    # --------------------------------------------------------

    student_name = models.CharField(
        max_length=100
    )

    mobile = models.CharField(
        max_length=15
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # COURSE
    # --------------------------------------------------------

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admissions"
    )

    # --------------------------------------------------------
    # BRANCH
    # --------------------------------------------------------

    branch = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # ADMISSION DATE
    # --------------------------------------------------------

    admission_date = models.DateField(
        default=timezone.localdate
    )

    # --------------------------------------------------------
    # FEES
    # --------------------------------------------------------

    total_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    paid_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # --------------------------------------------------------
    # INITIAL PAYMENT MODE
    # --------------------------------------------------------

    initial_payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES,
        default="cash"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    # --------------------------------------------------------
    # NOTES
    # --------------------------------------------------------

    notes = models.TextField(
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # CREATED BY
    # --------------------------------------------------------

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_admissions"
    )

    # --------------------------------------------------------
    # CREATED DATE
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def save(self, *args, **kwargs):

        # Generate Admission Number
        if not self.admission_number:

            last_admission = (
                Admission.objects
                .order_by("-id")
                .first()
            )

            if last_admission:

                next_number = (
                    last_admission.id + 1
                )

            else:

                next_number = 1

            self.admission_number = (
                f"MCTI{next_number:05d}"
            )

        # Payment Status
        if self.paid_fee <= 0:

            self.payment_status = "pending"

        elif self.paid_fee >= self.total_fee:

            self.payment_status = "paid"

        else:

            self.payment_status = "partial"

        super().save(
            *args,
            **kwargs
        )

    # --------------------------------------------------------
    # BALANCE FEE
    # --------------------------------------------------------

    @property
    def balance_fee(self):

        balance = (
            self.total_fee -
            self.paid_fee
        )

        return max(balance, 0)

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    def __str__(self):

        return (
            f"{self.admission_number} - "
            f"{self.student_name}"
        )

    class Meta:

        ordering = [
            "-created_at"
        ]


# ============================================================
# STUDENT
# ============================================================

class Student(models.Model):

    STATUS_CHOICES = [

        ("active", "Active"),

        ("completed", "Completed"),

        ("dropout", "Dropout"),

        ("inactive", "Inactive"),

    ]

    # --------------------------------------------------------
    # LOGIN USER
    # --------------------------------------------------------
    # This connects Django User with actual Student record.
    #
    # Student Login
    #       ↓
    # Django User
    #       ↓
    # Student
    # --------------------------------------------------------

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="student_account"
    )

    # --------------------------------------------------------
    # STUDENT ID
    # --------------------------------------------------------

    student_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    # --------------------------------------------------------
    # LINK WITH ADMISSION
    # --------------------------------------------------------

    admission = models.OneToOneField(
        Admission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student"
    )

    # --------------------------------------------------------
    # STUDENT INFORMATION
    # --------------------------------------------------------

    name = models.CharField(
        max_length=100
    )

    mobile = models.CharField(
        max_length=15
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # COURSE
    # --------------------------------------------------------

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )

    # --------------------------------------------------------
    # BRANCH
    # --------------------------------------------------------

    branch = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # JOINING DATE
    # --------------------------------------------------------

    joining_date = models.DateField(
        default=timezone.localdate
    )

    # --------------------------------------------------------
    # STUDENT STATUS
    # --------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    # --------------------------------------------------------
    # TRAINER
    # --------------------------------------------------------

    trainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )

    # --------------------------------------------------------
    # NOTES
    # --------------------------------------------------------

    notes = models.TextField(
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # CREATED BY
    # --------------------------------------------------------

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_students"
    )

    # --------------------------------------------------------
    # CREATED DATE
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def save(self, *args, **kwargs):

        if not self.student_id:

            last_student = (
                Student.objects
                .order_by("-id")
                .first()
            )

            if last_student:

                next_number = (
                    last_student.id + 1
                )

            else:

                next_number = 1

            self.student_id = (
                f"MCTI-STU-{next_number:05d}"
            )

        super().save(
            *args,
            **kwargs
        )

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    def __str__(self):

        return (
            f"{self.student_id} - "
            f"{self.name}"
        )

    class Meta:

        ordering = [
            "-created_at"
        ]


# ============================================================
# FEE PAYMENT
# ============================================================

class FeePayment(models.Model):

    PAYMENT_MODE_CHOICES = [

        ("cash", "Cash"),

        ("upi", "UPI"),

        ("bank", "Bank Transfer"),

        ("card", "Card"),

        ("cheque", "Cheque"),

    ]

    # --------------------------------------------------------
    # RECEIPT NUMBER
    # --------------------------------------------------------

    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="fee_payments"
    )

    # --------------------------------------------------------
    # PAYMENT DATE
    # --------------------------------------------------------

    payment_date = models.DateField(
        default=timezone.localdate
    )

    # --------------------------------------------------------
    # AMOUNT
    # --------------------------------------------------------

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # --------------------------------------------------------
    # PAYMENT HISTORY
    # --------------------------------------------------------

    previous_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    balance_after_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # --------------------------------------------------------
    # PAYMENT MODE
    # --------------------------------------------------------

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES,
        default="cash"
    )

    # --------------------------------------------------------
    # TRANSACTION / REFERENCE
    # --------------------------------------------------------

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # REMARKS
    # --------------------------------------------------------

    remarks = models.TextField(
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # COLLECTED BY
    # --------------------------------------------------------

    collected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collected_fee_payments"
    )

    # --------------------------------------------------------
    # CREATED DATE
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def save(self, *args, **kwargs):

        # ----------------------------------------------------
        # RECEIPT NUMBER
        # ----------------------------------------------------

        if not self.receipt_number:

            last_payment = (
                FeePayment.objects
                .order_by("-id")
                .first()
            )

            if last_payment:

                next_number = (
                    last_payment.id + 1
                )

            else:

                next_number = 1

            self.receipt_number = (
                f"MCTI-RCP-{next_number:05d}"
            )

        # ----------------------------------------------------
        # PREVIOUS PAID
        # ----------------------------------------------------

        previous_paid = sum(
            payment.amount
            for payment in FeePayment.objects.filter(
                student=self.student
            ).exclude(
                pk=self.pk
            )
        )

        self.previous_paid = previous_paid

        # ----------------------------------------------------
        # BALANCE AFTER PAYMENT
        # ----------------------------------------------------

        if self.student.admission:

            total_fee = (
                self.student.admission.total_fee
            )

            balance = (
                total_fee
                - previous_paid
                - self.amount
            )

            self.balance_after_payment = max(
                balance,
                0
            )

        else:

            self.balance_after_payment = 0

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        super().save(
            *args,
            **kwargs
        )

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    def __str__(self):

        return (
            f"{self.receipt_number} - "
            f"{self.student.name} - "
            f"₹{self.amount}"
        )

    class Meta:

        ordering = [
            "-payment_date",
            "-created_at"
        ]


# ============================================================
# AUTOMATIC STUDENT CREATION FROM ADMISSION
# ============================================================

@receiver(post_save, sender=Admission)
def create_student_from_admission(
    sender,
    instance,
    created,
    **kwargs
):

    if created:

        Student.objects.create(
            admission=instance,
            name=instance.student_name,
            mobile=instance.mobile,
            email=instance.email,
            course=instance.course,
            branch=instance.branch,
            joining_date=instance.admission_date,
            status="active",
            created_by=instance.created_by,
        )


# ============================================================
# AUTO CREATE INITIAL RECEIPT FROM ADMISSION
# ============================================================

@receiver(post_save, sender=Admission)
def create_initial_fee_payment(
    sender,
    instance,
    created,
    **kwargs
):

    if created and instance.paid_fee > 0:

        student = getattr(
            instance,
            "student",
            None
        )

        if student:

            FeePayment.objects.create(
                student=student,
                payment_date=instance.admission_date,
                amount=instance.paid_fee,
                payment_mode=instance.initial_payment_mode,
                collected_by=instance.created_by,
                remarks="Initial payment at admission"
            )

class StaffProfile(models.Model):

    BRANCH_CHOICES = [
        ("kharghar", "Kharghar"),
        ("panvel", "Panvel"),
        ("koperkhairane", "Koperkhairane"),
        ("kamothe", "Kamothe"),
        ("ghansoli", "Ghansoli"),
        ("nerul", "Nerul"),
        ("head_office", "Head Office"),
    ]

    DEPARTMENT_CHOICES = [
        ("management", "Management"),
        ("sales", "Sales"),
        ("marketing", "Marketing"),
        ("training", "Training"),
        ("operations", "Operations"),
        ("hr", "HR"),
        ("accounts", "Accounts"),
        ("placement", "Placement"),
        ("it", "IT"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )

    branch = models.CharField(
        max_length=50,
        choices=BRANCH_CHOICES
    )

    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES
    )

    designation = models.CharField(
        max_length=100
    )

    joining_date = models.DateField(
        default=timezone.now
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.designation}"
        )
# ============================================================
# AUTO UPDATE ADMISSION FEES AFTER PAYMENT
# ============================================================

@receiver(post_save, sender=FeePayment)
def update_admission_fees(
    sender,
    instance,
    created,
    **kwargs
):

    admission = (
        instance.student.admission
    )

    if admission:

        total_paid = sum(
            payment.amount
            for payment in instance.student.fee_payments.all()
        )

        # Avoid unnecessary save if value is already same
        if admission.paid_fee != total_paid:

            admission.paid_fee = total_paid

            admission.save(
                update_fields=[
                    "paid_fee",
                    "payment_status"
                ]
            )

