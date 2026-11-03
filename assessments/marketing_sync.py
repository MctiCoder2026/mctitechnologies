"""Sync completed assessments to HO-assigned Outreach branches."""
import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

VALID_BRANCHES = {
    "kharghar", "panvel", "koperkhairane",
    "kamothe", "ghansoli", "nerul",
}

def sync_one(kind, attempt_id, source_type, source_id):
    from core.models import OutreachContact
    from career_tools.models import (
        AssessmentBranchAssignment,
        AssessmentBranchAssignmentLog,
    )

    contacts = list(
        OutreachContact.objects.filter(
            contact_type="marketing_lead",
            source_type=source_type,
            source_record_id=source_id,
            branch__in=VALID_BRANCHES,
        ).order_by("pk").values_list("branch", "pushed_by_id")
    )

    branches = {branch for branch, _ in contacts}
    if not branches:
        return "unmatched"
    if len(branches) != 1:
        return "conflict"

    branch = next(iter(branches))
    actor_id = contacts[0][1]

    with transaction.atomic():
        record, created = AssessmentBranchAssignment.objects.get_or_create(
            kind=kind,
            attempt_id=attempt_id,
            defaults={
                "branch": branch,
                "assigned_by_id": actor_id,
            },
        )

        if not created:
            return "existing" if record.branch == branch else "conflict"

        AssessmentBranchAssignmentLog.objects.create(
            kind=kind,
            attempt_id=attempt_id,
            old_branch="",
            new_branch=branch,
            changed_by_id=actor_id,
        )
    return "created"

def sync_assessment(attempt_id):
    from assessments.models import AssessmentAttempt, ScholarshipResult

    attempt = AssessmentAttempt.objects.select_related(
        "assessment"
    ).filter(pk=attempt_id, status="completed").first()

    if not attempt:
        return "not_completed"

    slug = attempt.assessment.slug

    if slug in {
        "ai-ready-maharashtra-2026",
        "ai-ready-maharashtra-2026-marathi",
    }:
        return sync_one("ai", attempt.pk, "ai_ready", attempt.pk)

    if slug == "mcti-scholarship-test-2026":
        result_id = ScholarshipResult.objects.filter(
            attempt_id=attempt.pk
        ).values_list("pk", flat=True).first()
        if result_id:
            return sync_one(
                "scholarship", attempt.pk, "scholarship", result_id
            )
        return "unmatched"

    return "not_applicable"

def sync_aptitude(attempt_id):
    from career_tools.models import AptitudeAttempt

    attempt = AptitudeAttempt.objects.filter(
        pk=attempt_id,
        status="completed",
    ).first()

    if not attempt:
        return "not_completed"

    return sync_one(
        "aptitude", attempt.pk, "aptitude", attempt.profile_id
    )

def safe_sync(fn, pk):
    try:
        result = fn(pk)
        if result == "conflict":
            logger.warning(
                "Assessment auto-sync branch conflict: %s:%s",
                fn.__name__, pk,
            )
    except Exception:
        logger.exception(
            "Assessment auto-sync failed: %s:%s",
            fn.__name__, pk,
        )

@receiver(
    post_save,
    sender="assessments.AssessmentAttempt",
    dispatch_uid="mcti_marketing_assessment_completion_v1",
)
def assessment_completed(sender, instance, **kwargs):
    if instance.status == "completed":
        transaction.on_commit(
            lambda pk=instance.pk: safe_sync(sync_assessment, pk)
        )

@receiver(
    post_save,
    sender="career_tools.AptitudeAttempt",
    dispatch_uid="mcti_marketing_aptitude_completion_v1",
)
def aptitude_completed(sender, instance, **kwargs):
    if instance.status == "completed":
        transaction.on_commit(
            lambda pk=instance.pk: safe_sync(sync_aptitude, pk)
        )
