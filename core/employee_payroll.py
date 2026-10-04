from datetime import date
from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    StaffProfile, EmployeePayrollProfile, EmployeeMonthlySalary,
    EmployeeSalaryIssue, EmployeeSalaryReply,
)
from lms.models import ClassroomTrainer
from .views import can_view_business_amounts, get_user_branch


def manager_access(user):
    return can_view_business_amounts(user)


def profiles_for(user):
    records = EmployeePayrollProfile.objects.select_related("user")
    if user.is_superuser:
        return records
    return records.filter(branch__iexact=get_user_branch(user) or "__none__")


class ProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(), required=False,
        label="Existing staff / trainer login",
    )
    new_username = forms.CharField(
        required=False, max_length=150, label="New login username",
    )
    new_password = forms.CharField(
        required=False, widget=forms.PasswordInput,
        label="New login password",
    )

    class Meta:
        model = EmployeePayrollProfile
        fields = [
            "user", "name", "branch", "designation",
            "employment_type", "joining_date",
        ]
        widgets = {
            "joining_date": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date"}
            )
        }

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        users = get_user_model().objects.filter(is_active=True)
        workers = Q(
            staff_profile__is_active=True, is_staff=True
        ) | Q(classroom_trainer_profile__is_active=True)
        users = users.filter(workers)
        if not actor.is_superuser:
            branch = get_user_branch(actor)
            users = users.filter(
                Q(staff_profile__branch__iexact=branch)
                | Q(classroom_trainer_profile__branch__iexact=branch)
            )
            self.fields["branch"].initial = branch
            self.fields["branch"].disabled = True
        self.fields["user"].queryset = users.distinct().order_by("username")
        if self.instance.pk:
            self.fields["user"].queryset = get_user_model().objects.filter(
                pk=self.instance.user_id,
            )
            self.fields["user"].disabled = True
            self.fields["branch"].disabled = True
            self.fields.pop("new_username")
            self.fields.pop("new_password")

    def clean(self):
        data = super().clean()
        branch = (data.get("branch") or "").strip().lower()
        valid = {v for v, label in StaffProfile.BRANCH_CHOICES}
        if branch not in valid:
            self.add_error("branch", "Select a valid branch.")
        data["branch"] = branch
        if self.instance.pk:
            return data
        user = data.get("user")
        username = (data.get("new_username") or "").strip().lower()
        password = data.get("new_password") or ""
        if user:
            if username or password:
                self.add_error("user", "Select an existing login OR enter a new login.")
            if EmployeePayrollProfile.objects.filter(user=user).exists():
                self.add_error("user", "This login already has an employee profile.")
            same_branch = (
                StaffProfile.objects.filter(
                    user=user, is_active=True, branch__iexact=branch,
                ).exists()
                or ClassroomTrainer.objects.filter(
                    user=user, is_active=True, branch__iexact=branch,
                ).exists()
            )
            if not same_branch:
                self.add_error("user", "Login and employee branch must match.")
        else:
            if not username:
                self.add_error("new_username", "Enter a username for the new account.")
            elif get_user_model().objects.filter(username__iexact=username).exists():
                self.add_error("new_username", "Username already exists.")
            if len(password) < 10:
                self.add_error("new_password", "Use at least 10 characters.")
            else:
                candidate = get_user_model()(username=username)
                try:
                    validate_password(password, candidate)
                except ValidationError as exc:
                    self.add_error("new_password", exc)
            if data.get("employment_type") not in ("trainer", "intern", "part_time"):
                self.add_error(
                    "employment_type",
                    "New accounts here are for trainer/intern/part-time training. "
                    "Create office staff through the existing staff setup.",
                )
        if data.get("joining_date") and data["joining_date"] > timezone.localdate():
            self.add_error("joining_date", "Joining date cannot be in the future.")
        return data


class SalaryForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=EmployeePayrollProfile.objects.none(),
    )
    month = forms.DateField(
        label="Salary month: select its first day",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    basic_amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0,
        label="Basic salary / stipend",
    )
    allowances = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0, initial=0,
    )
    deductions = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0, initial=0,
    )
    note = forms.CharField(
        required=False, max_length=2000,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Allowance / deduction explanation",
    )

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].queryset = profiles_for(actor)

    def clean(self):
        data = super().clean()
        month = data.get("month")
        if month and month.day != 1:
            self.add_error("month", "Select the first day of the salary month.")
        values = [data.get(k) for k in ("basic_amount", "allowances", "deductions")]
        if all(v is not None for v in values):
            if values[2] > values[0] + values[1]:
                self.add_error("deductions", "Deductions exceed earnings.")
            if (values[1] or values[2]) and not (data.get("note") or "").strip():
                self.add_error("note", "Explain the allowance or deduction.")
        return data


@login_required
def manage_payroll(request):
    if not manager_access(request.user):
        return HttpResponseForbidden("Branch head / power user access required.")
    records = profiles_for(request.user)
    selected = None
    edit_id = request.GET.get("edit")
    if edit_id:
        selected = get_object_or_404(records, pk=edit_id)

    profile_form = ProfileForm(instance=selected, actor=request.user)
    salary_form = SalaryForm(actor=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "profile":
            profile_form = ProfileForm(
                request.POST, instance=selected, actor=request.user,
            )
            if profile_form.is_valid():
                try:
                    with transaction.atomic():
                        employee = profile_form.save(commit=False)
                        if not selected:
                            user = profile_form.cleaned_data.get("user")
                            if not user:
                                user = get_user_model().objects.create_user(
                                    username=profile_form.cleaned_data["new_username"].strip().lower(),
                                    password=profile_form.cleaned_data["new_password"],
                                )
                                ClassroomTrainer.objects.create(
                                    user=user, name=employee.name,
                                    branch=employee.branch,
                                )
                            employee.user = user
                            employee.created_by = request.user
                        employee.save()
                    messages.success(request, "Employee profile saved.")
                    return redirect("branch_employee_payroll")
                except IntegrityError:
                    profile_form.add_error(None, "Login/profile already exists. Reload and select it.")

        elif action == "salary":
            salary_form = SalaryForm(request.POST, actor=request.user)
            if salary_form.is_valid():
                data = salary_form.cleaned_data
                with transaction.atomic():
                    employee = get_object_or_404(
                        profiles_for(request.user).select_for_update(),
                        pk=data["employee"].pk,
                    )
                    salary = EmployeeMonthlySalary.objects.filter(
                        employee=employee, month=data["month"],
                    ).first()
                    if salary and salary.status != "draft":
                        salary_form.add_error(None, "Published salary is locked. Use the issue thread.")
                    else:
                        if salary is None:
                            salary = EmployeeMonthlySalary(
                                employee=employee, month=data["month"],
                            )
                        for field in ("basic_amount", "allowances", "deductions", "note"):
                            setattr(salary, field, data[field])
                        salary.updated_by = request.user
                        salary.save()
                        messages.success(request, "Salary draft saved.")
                        return redirect("branch_employee_payroll")

        elif action in ("publish", "paid"):
            with transaction.atomic():
                salary = get_object_or_404(
                    EmployeeMonthlySalary.objects.select_for_update(),
                    pk=request.POST.get("salary_id"),
                    employee__in=records,
                )
                if action == "publish":
                    if salary.status != "draft":
                        return HttpResponseForbidden("Only drafts can be published.")
                    salary.status = "published"
                    salary.published_by = request.user
                    salary.published_at = timezone.now()
                    salary.save(update_fields=["status", "published_by", "published_at", "updated_at"])
                else:
                    if salary.status != "published":
                        return HttpResponseForbidden("Publish salary before recording payment.")
                    try:
                        paid_on = date.fromisoformat(request.POST.get("paid_on", ""))
                    except ValueError:
                        return HttpResponseForbidden("Enter a valid payment date.")
                    reference = request.POST.get("payment_reference", "").strip()
                    if paid_on > timezone.localdate() or len(reference) < 3 or len(reference) > 200:
                        return HttpResponseForbidden("Enter actual payment date and mode/reference.")
                    salary.status = "paid"
                    salary.paid_on = paid_on
                    salary.payment_reference = reference
                    salary.paid_by = request.user
                    salary.save(update_fields=[
                        "status", "paid_on", "payment_reference", "paid_by", "updated_at",
                    ])
            return redirect("branch_employee_payroll")

        elif action == "reply":
            text = request.POST.get("reply", "").strip()
            status = request.POST.get("status")
            if len(text) < 5 or len(text) > 2000 or status not in ("replied", "resolved"):
                return HttpResponseForbidden("Enter a reply and valid status.")
            with transaction.atomic():
                issue = get_object_or_404(
                    EmployeeSalaryIssue.objects.select_for_update(),
                    pk=request.POST.get("issue_id"),
                    salary__employee__in=records,
                )
                EmployeeSalaryReply.objects.create(
                    issue=issue, author=request.user, message=text,
                )
                issue.status = status
                issue.save(update_fields=["status"])
            return redirect("branch_employee_payroll")
        else:
            return HttpResponseForbidden("Invalid action.")

    salaries = EmployeeMonthlySalary.objects.filter(
        employee__in=records,
    ).select_related("employee").order_by("-month", "-pk")
    issues = EmployeeSalaryIssue.objects.filter(
        salary__employee__in=records,
    ).select_related("salary__employee").prefetch_related("replies__author")
    return render(request, "core/employee_payroll.html", {
        "manager": True, "profiles": records.order_by("name"),
        "profile_form": profile_form, "salary_form": salary_form,
        "salaries": salaries[:100], "issues": issues[:100],
        "today": timezone.localdate(),
        "open_issues": issues.exclude(status="resolved").count(),
    })


@login_required(login_url="/lms/classroom/trainer-login/")
def my_payroll(request):
    employee = EmployeePayrollProfile.objects.filter(
        user=request.user, user__is_active=True,
    ).first()
    if request.method == "POST":
        if not employee:
            return HttpResponseForbidden("Employee profile is not configured.")
        salary = get_object_or_404(
            EmployeeMonthlySalary,
            pk=request.POST.get("salary_id"), employee=employee,
            status__in=("published", "paid"),
        )
        text = request.POST.get("message", "").strip()
        if len(text) < 5 or len(text) > 2000:
            return HttpResponseForbidden("Enter a salary issue note of 5–2000 characters.")
        EmployeeSalaryIssue.objects.create(salary=salary, message=text)
        messages.success(request, "Issue submitted to your branch head and power user.")
        return redirect("employee_my_payroll")

    salaries = EmployeeMonthlySalary.objects.filter(
        employee=employee, status__in=("published", "paid"),
    ) if employee else EmployeeMonthlySalary.objects.none()
    issues = EmployeeSalaryIssue.objects.filter(
        salary__employee=employee,
    ).select_related("salary").prefetch_related("replies__author") if employee else []
    return render(request, "core/employee_payroll.html", {
        "manager": False, "employee": employee,
        "salaries": salaries, "issues": issues,
    })
