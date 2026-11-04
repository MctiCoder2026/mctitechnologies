from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.shortcuts import render
from core.views import get_user_branch, is_admin_user
from .models import AlumniContact

ALUMNI_BRANCHES = ("kharghar", "panvel", "koperkhairane")


@login_required(login_url="/staff-login/")
def dashboard(request):
    admin = is_admin_user(request.user)

    if admin:
        contacts = AlumniContact.objects.filter(
            branch__in=ALUMNI_BRANCHES
        )
        branch = request.GET.get("branch", "")
        if branch in ALUMNI_BRANCHES:
            contacts = contacts.filter(branch=branch)
    else:
        branch = get_user_branch(request.user)
        if branch not in ALUMNI_BRANCHES:
            raise PermissionDenied
        contacts = AlumniContact.objects.filter(branch=branch)

    total = contacts.count()

    alumni_tab = request.GET.get("tab", "pending")
    if alumni_tab not in ("pending", "interested", "do_not_contact", "contact_issues", "all"):
        alumni_tab = "pending"

    issue_statuses = ("invalid_number", "not_in_service")

    if alumni_tab == "pending":
        contacts = contacts.filter(
            permission_status="unknown"
        ).exclude(
            status__in=("do_not_contact", *issue_statuses)
        )
    elif alumni_tab == "interested":
        contacts = contacts.filter(
            permission_status="allowed"
        ).exclude(
            status__in=("do_not_contact", *issue_statuses)
        )
    elif alumni_tab == "do_not_contact":
        contacts = contacts.filter(
            Q(status="do_not_contact") |
            Q(permission_status="declined")
        )
    elif alumni_tab == "contact_issues":
        contacts = contacts.filter(
            status__in=issue_statuses
        ).exclude(
            Q(status="do_not_contact") |
            Q(permission_status="declined")
        )

    year = request.GET.get("year", "")
    status = request.GET.get("status", "")
    course = request.GET.get("course", "").strip()
    search = request.GET.get("search", "").strip()

    if year.isdigit() and 2013 <= int(year) <= 2025:
        contacts = contacts.filter(admission_year=int(year))

    valid_statuses = dict(AlumniContact.STATUS_CHOICES)
    if status in valid_statuses:
        contacts = contacts.filter(status=status)

    if course:
        contacts = contacts.filter(previous_course__icontains=course)

    if search:
        contacts = contacts.filter(
            Q(name__icontains=search) |
            Q(mobile__icontains=search)
        )

    contacts = contacts.annotate(
        message_count=Count("message_activities")
    ).order_by("-created_at")
    filtered_total = contacts.count()
    paginator = Paginator(contacts, 100)
    page_obj = paginator.get_page(request.GET.get("page"))
    contacts = page_obj.object_list

    query_params = request.GET.copy()
    prev_url = next_url = ""
    if page_obj.has_previous():
        query_params["page"] = page_obj.previous_page_number()
        prev_url = "?" + query_params.urlencode()
    if page_obj.has_next():
        query_params["page"] = page_obj.next_page_number()
        next_url = "?" + query_params.urlencode()

    return render(request, "alumni/dashboard.html", {
        "contacts": contacts,
        "total": total,
        "alumni_tab": alumni_tab,
        "is_admin": admin,
        "selected_branch": branch,
        "selected_year": year,
        "selected_status": status,
        "course": course,
        "search": search,
        "branches": AlumniContact.BRANCH_CHOICES,
        "statuses": AlumniContact.STATUS_CHOICES,
        "years": range(2025, 2012, -1),
        "page_obj": page_obj,
        "filtered_total": filtered_total,
        "prev_url": prev_url,
        "next_url": next_url,
        "permissions": AlumniContact.PERMISSION_CHOICES,
    })


# Independent historical alumni import. Never writes to CRM/admissions.
import io
import json
import secrets
from django.contrib import messages
from django.core.cache import caches
alumni_cache = caches['alumni_import']
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.utils.html import format_html
from openpyxl import load_workbook
from .import_utils import normalize_mobile, parse_year, validate_mapping

MAX_XLSX_BYTES = 5 * 1024 * 1024
MAX_IMPORT_ROWS = 10000
ALUMNI_FIELDS = ('name', 'mobile', 'previous_course', 'admission_year', 'email')


def _import_scope(user):
    if is_admin_user(user):
        return True, None
    branch = get_user_branch(user)
    if branch not in ALUMNI_BRANCHES:
        raise PermissionDenied
    return False, branch


def _sheet_rows(payload, sheet_name):
    workbook = load_workbook(io.BytesIO(payload), read_only=True, data_only=True)
    try:
        if sheet_name not in workbook.sheetnames:
            raise ValueError('Selected sheet not found')
        sheet = workbook[sheet_name]
        rows = sheet.iter_rows(values_only=True)
        header = next(rows, ())
        headers = [str(v).strip() if v is not None else '' for v in header]
        if len(headers) > 150:
            raise ValueError('Too many Excel columns')
        return headers, list(rows)
    finally:
        workbook.close()


def _review(payload, sheet_name, mapping, branch):
    validate_mapping(mapping)
    headers, rows = _sheet_rows(payload, sheet_name)
    if any(index >= len(headers) for index in mapping.values()):
        raise ValueError('Mapping column is outside Excel header')
    if len(rows) > MAX_IMPORT_ROWS:
        raise ValueError('Maximum 10,000 data rows per import')
    records = []
    preview = []
    seen = set()
    invalid = 0
    duplicates_in_file = 0
    existing = set(AlumniContact.objects.filter(branch=branch).exclude(normalized_mobile='').values_list('normalized_mobile', flat=True))
    duplicates_in_db = 0
    for number, row in enumerate(rows, 2):
        if not any(v is not None and str(v).strip() for v in row):
            continue
        data = {field: (row[idx] if idx < len(row) else None) for field, idx in mapping.items()}
        name = str(data.get('name') or '').strip()
        mobile = normalize_mobile(data.get('mobile'))
        course = str(data.get('previous_course') or '').strip()
        email = str(data.get('email') or '').strip()
        year = None
        error = ''
        try:
            if 'admission_year' in mapping:
                year = parse_year(data.get('admission_year'))
        except ValueError as exc:
            error = str(exc)
        if not name or len(name) > 150 or not mobile or len(course) > 200 or len(email) > 254:
            error = error or 'Missing/invalid name, mobile, course or email'
        if mobile in seen and not error:
            error = 'Duplicate mobile in uploaded file'
            duplicates_in_file += 1
        if mobile in existing and not error:
            error = 'Mobile already exists in this branch'
            duplicates_in_db += 1
        if error:
            invalid += 1
        else:
            seen.add(mobile)
            records.append(AlumniContact(name=name, mobile=mobile, normalized_mobile=mobile, branch=branch, previous_course=course, admission_year=year, email=email, source_file='Excel import'))
        if len(preview) < 30:
            preview.append({'row': number, 'name': name, 'mobile': mobile, 'course': course, 'year': year, 'error': error or 'Ready'})
    return {'records': records, 'preview': preview, 'invalid': invalid, 'duplicates_in_file': duplicates_in_file, 'duplicates_in_db': duplicates_in_db, 'total_rows': len(rows)}


@login_required(login_url='/staff-login/')
@require_http_methods(['GET', 'POST'])
def import_excel(request):
    admin, staff_branch = _import_scope(request.user)
    state = {'stage': 'upload', 'branches': AlumniContact.BRANCH_CHOICES, 'admin': admin, 'fields': ALUMNI_FIELDS}
    if request.method == 'GET':
        return render(request, 'alumni/import.html', state)
    action = request.POST.get('action')
    if action == 'upload':
        upload = request.FILES.get('file')
        branch = request.POST.get('branch') if admin else staff_branch
        if branch not in ALUMNI_BRANCHES:
            messages.error(request, 'Choose a valid branch')
            return redirect('alumni:import')
        if not upload or not upload.name.lower().endswith('.xlsx') or upload.size > MAX_XLSX_BYTES or upload.size == 0:
            messages.error(request, 'Upload a valid .xlsx file up to 5 MB')
            return redirect('alumni:import')
        payload = upload.read()
        try:
            workbook = load_workbook(io.BytesIO(payload), read_only=True, data_only=True)
            sheets = []
            try:
                for sheet in workbook.worksheets:
                    headers = [str(v).strip() if v is not None else '' for v in next(sheet.iter_rows(max_row=1, values_only=True), ())]
                    sheets.append({'name': sheet.title, 'headers': list(enumerate(headers))})
            finally:
                workbook.close()
        except Exception:
            messages.error(request, 'Could not read Excel file')
            return redirect('alumni:import')
        token = secrets.token_urlsafe(24)
        alumni_cache.set('alumni_import_'+token, {'payload': payload, 'branch': branch, 'sheets': sheets, 'user': request.user.pk}, timeout=900)
        state.update(stage='mapping', token=token, sheets=sheets, branch=branch)
        return render(request, 'alumni/import.html', state)
    token = request.POST.get('token', '')
    if not token or len(token) > 100:
        return HttpResponseBadRequest('Invalid upload token')
    stored = alumni_cache.get('alumni_import_'+token)
    if not stored or stored['user'] != request.user.pk:
        messages.error(request, 'Upload expired. Please upload again.')
        return redirect('alumni:import')
    branch = stored['branch']
    if not admin and branch != staff_branch:
        raise PermissionDenied
    if action == 'preview':
        sheet = request.POST.get('sheet', '')
        mapping = {}
        for field in ALUMNI_FIELDS:
            index = request.POST.get('map_'+field, '')
            if index != '':
                if not index.isdigit():
                    return HttpResponseBadRequest('Invalid column index')
                mapping[field] = int(index)
        try:
            review = _review(stored['payload'], sheet, mapping, branch)
        except (ValueError, TypeError) as exc:
            messages.error(request, str(exc))
            return redirect('alumni:import')
        stored.update(sheet=sheet, mapping=mapping)
        alumni_cache.set('alumni_import_'+token, stored, timeout=900)
        state.update(stage='preview', token=token, branch=branch, review=review)
        return render(request, 'alumni/import.html', state)
    if action == 'confirm':
        if 'sheet' not in stored or 'mapping' not in stored:
            return HttpResponseBadRequest('Preview required')
        try:
            review = _review(stored['payload'], stored['sheet'], stored['mapping'], branch)
        except (ValueError, TypeError) as exc:
            messages.error(request, str(exc))
            return redirect('alumni:import')
        created = 0
        # Serialize concurrent imports per branch with a database advisory lock on PostgreSQL.
        # Duplicate detection is repeated inside transaction; no existing records updated.
        with transaction.atomic():
            from django.db import connection

            # One transaction-scoped lock per alumni branch.
            lock_id = {
                'kharghar': 810001,
                'panvel': 810002,
                'koperkhairane': 810003,
            }[branch]

            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT pg_advisory_xact_lock(%s)',
                    [lock_id],
                )

            for obj in review['records']:
                if not AlumniContact.objects.filter(
                    branch=branch,
                    normalized_mobile=obj.normalized_mobile
                ).exists():
                    obj.save()
                    created += 1
        alumni_cache.delete('alumni_import_'+token)
        messages.success(request, f'Imported {created} alumni. Skipped {review["invalid"]} invalid/duplicate rows and {len(review["records"])-created} existing records.')
        return redirect('alumni:dashboard')
    return HttpResponseBadRequest('Invalid action')


@login_required(login_url="/staff-login/")
@require_http_methods(["POST"])
def update_contact(request, contact_id):
    from datetime import date
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from django.urls import reverse
    from django.http import HttpResponseRedirect
    from urllib.parse import parse_qsl, urlencode

    admin, staff_branch = _import_scope(request.user)

    queryset = AlumniContact.objects.filter(branch__in=ALUMNI_BRANCHES)
    if not admin:
        queryset = queryset.filter(branch=staff_branch)

    contact = get_object_or_404(queryset, pk=contact_id)

    new_status = request.POST.get("status", "")
    new_permission = request.POST.get("permission_status", "")
    remarks = request.POST.get("remarks", "").strip()
    followup_raw = request.POST.get("followup_date", "").strip()

    if new_status not in dict(AlumniContact.STATUS_CHOICES):
        messages.error(request, "Invalid alumni status.")
        return redirect("alumni:dashboard")

    if new_permission not in dict(AlumniContact.PERMISSION_CHOICES):
        messages.error(request, "Invalid permission status.")
        return redirect("alumni:dashboard")

    if len(remarks) > 5000:
        messages.error(request, "Remarks must be under 5,000 characters.")
        return redirect("alumni:dashboard")

    if new_permission == "allowed" and request.POST.get("consent_confirmed") != "yes":
        messages.error(
            request,
            "Confirm that the alumnus has given permission before enabling WhatsApp."
        )
        return redirect("alumni:dashboard")

    followup_date = None
    if followup_raw:
        try:
            followup_date = date.fromisoformat(followup_raw)
        except ValueError:
            messages.error(request, "Invalid follow-up date.")
            return redirect("alumni:dashboard")

    old_status = contact.status
    contact.status = new_status
    contact.permission_status = new_permission
    contact.remarks = remarks
    contact.followup_date = followup_date

    update_fields = [
        "status", "permission_status", "remarks",
        "followup_date", "updated_at"
    ]

    if new_status == "contacted" and old_status != "contacted":
        contact.last_contacted_at = timezone.now()
        update_fields.append("last_contacted_at")

    contact.save(update_fields=update_fields)
    messages.success(request, f"Updated alumni record: {contact.name}")

    allowed_filters = {"tab", "branch", "year", "status", "course", "search", "page"}
    raw_query = request.POST.get("return_query", "")
    filters = [
        (key, value)
        for key, value in parse_qsl(raw_query, keep_blank_values=True)
        if key in allowed_filters
    ]
    query_string = urlencode(filters)
    dashboard_url = reverse("alumni:dashboard")
    return HttpResponseRedirect(
        dashboard_url + ("?" + query_string if query_string else "")
    )


@login_required(login_url="/staff-login/")
@require_http_methods(["POST"])
def confirm_message(request, contact_id):
    """Record staff-confirmed WhatsApp sending, not actual delivery."""
    import uuid

    from django.db import IntegrityError, transaction
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404

    from .models import AlumniMessageActivity

    admin, staff_branch = _import_scope(request.user)

    queryset = AlumniContact.objects.filter(branch__in=ALUMNI_BRANCHES)
    if not admin:
        queryset = queryset.filter(branch=staff_branch)

    message_type = request.POST.get("message_type", "")
    language = request.POST.get("language", "")
    raw_token = request.POST.get("confirmation_token", "")

    if message_type not in dict(AlumniMessageActivity.MESSAGE_TYPES):
        return JsonResponse({"error": "Invalid message type"}, status=400)

    if language not in dict(AlumniMessageActivity.LANGUAGES):
        return JsonResponse({"error": "Invalid language"}, status=400)

    try:
        token = uuid.UUID(raw_token)
    except (ValueError, AttributeError, TypeError):
        return JsonResponse({"error": "Invalid confirmation token"}, status=400)

    with transaction.atomic():
        contact = get_object_or_404(
            queryset.select_for_update(),
            pk=contact_id,
        )

        if (
            contact.status in (
                "do_not_contact",
                "invalid_number",
                "not_in_service",
            )
            or contact.permission_status == "declined"
        ):
            return JsonResponse(
                {"error": "Contact is blocked"},
                status=403,
            )

        if not contact.normalized_mobile:
            return JsonResponse(
                {"error": "Mobile unavailable"},
                status=400,
            )

        if (
            message_type == "followup"
            and contact.permission_status != "allowed"
        ):
            return JsonResponse(
                {"error": "Follow-up requires permission"},
                status=403,
            )

        if (
            message_type == "permission"
            and contact.permission_status != "unknown"
        ):
            return JsonResponse(
                {"error": "Permission request not applicable"},
                status=403,
            )

        existing = AlumniMessageActivity.objects.filter(
            confirmation_token=token
        ).first()

        if existing:
            if (
                existing.alumni_id != contact.id
                or existing.staff_id != request.user.id
                or existing.message_type != message_type
                or existing.language != language
            ):
                return JsonResponse(
                    {"error": "Confirmation token conflict"},
                    status=409,
                )

            return JsonResponse({
                "success": True,
                "duplicate": True,
                "message_count": AlumniMessageActivity.objects.filter(
                    alumni=contact
                ).count(),
            })

        try:
            with transaction.atomic():
                AlumniMessageActivity.objects.create(
                    alumni=contact,
                    staff=request.user,
                    message_type=message_type,
                    language=language,
                    confirmation_token=token,
                )
        except IntegrityError:
            return JsonResponse(
                {"error": "Confirmation conflict; refresh and retry"},
                status=409,
            )

        count = AlumniMessageActivity.objects.filter(
            alumni=contact
        ).count()

    return JsonResponse({
        "success": True,
        "duplicate": False,
        "message_count": count,
    })
