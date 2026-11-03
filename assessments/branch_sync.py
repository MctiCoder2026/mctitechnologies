"""Automatic SSC branch assignment. Never changes exam results."""
import logging
import re
from collections import defaultdict

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

BRANCHES = {
    "kharghar", "panvel", "koperkhairane",
    "kamothe", "ghansoli", "nerul",
}

def mobile_key(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in "6789":
        return digits
    return None

def branch_map():
    from core.models import OutreachContact

    mapping = defaultdict(set)
    rows = OutreachContact.objects.filter(
        contact_type="marketing_lead",
        branch__in=BRANCHES,
    ).values_list("normalized_mobile", "branch")

    for mobile, branch in rows.iterator():
        key = mobile_key(mobile)
        if key:
            mapping[key].add(branch)

    return mapping

def sync_attempt(attempt_id, mapping=None):
    from assessments.models import AssessmentAttempt
    from career_tools.models import (
        AssessmentBranchAssignment,
        AssessmentBranchAssignmentLog,
    )

    attempt = AssessmentAttempt.objects.filter(
        pk=attempt_id,
        status="completed",
        assessment__assessment_type="exam_preparation",
        assessment__slug__startswith="ssc-",
    ).first()

    if not attempt:
        return "not_completed"

    key = mobile_key(attempt.participant_mobile)
    if not key:
        return "invalid_mobile"

    matches = (mapping if mapping is not None else branch_map()).get(
        key, set()
    )

    if len(matches) != 1:
        return "conflict" if matches else "unmatched"

    branch = next(iter(matches))

    with transaction.atomic():
        assignment, created = (
            AssessmentBranchAssignment.objects.get_or_create(
                kind="ssc",
                attempt_id=attempt.pk,
                defaults={
                    "branch": branch,
                    "assigned_by": None,
                },
            )
        )

        if not created:
            return "existing" if assignment.branch == branch else "conflict"

        AssessmentBranchAssignmentLog.objects.create(
            kind="ssc",
            attempt_id=attempt.pk,
            old_branch="",
            new_branch=branch,
            changed_by=None,
        )

    return "created"

def sync_mobile(mobile):
    from assessments.models import AssessmentAttempt

    key = mobile_key(mobile)
    if not key:
        return 0

    mapping = branch_map()
    if len(mapping.get(key, set())) != 1:
        return 0

    count = 0
    attempts = AssessmentAttempt.objects.filter(
        status="completed",
        assessment__assessment_type="exam_preparation",
        assessment__slug__startswith="ssc-",
    ).values_list("pk", "participant_mobile")

    for attempt_id, number in attempts.iterator():
        if mobile_key(number) == key:
            if sync_attempt(attempt_id, mapping) == "created":
                count += 1

    return count

@receiver(
    post_save,
    sender="assessments.AssessmentAttempt",
    dispatch_uid="mcti_ssc_autosync_20261017",
)
def on_ssc_completion(sender, instance, **kwargs):
    if instance.status != "completed":
        return

    try:
        if (
            instance.assessment.assessment_type == "exam_preparation"
            and instance.assessment.slug.startswith("ssc-")
        ):
            transaction.on_commit(
                lambda pk=instance.pk: safe_sync(pk)
            )
    except Exception:
        logger.exception("SSC auto-sync scheduling failed")

def safe_sync(attempt_id):
    try:
        sync_attempt(attempt_id)
    except Exception:
        logger.exception("SSC auto-sync failed: %s", attempt_id)
