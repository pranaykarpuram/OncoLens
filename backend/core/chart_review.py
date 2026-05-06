"""
Chart review eligibility, queue prioritization, and “since review” counters.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.utils import timezone

from evidence.models import Observation, SourceBackedObservation
from patients.models import ClinicalNote, Patient
from reports.models import DiagnosticReport

PARSE_NEEDS_QUEUE = ("pending", "needs_confirmation")


def normalized_review_status(patient: Patient) -> str:
    return (patient.review_status or "").replace("-", "_").lower()


def count_new_since_last_review(patient: Patient) -> Optional[Dict[str, Any]]:
    """
    Rough inventory of dated / ingested rows at or after last_chart_review_at.
    Returns None if no prior chart review logged.
    """
    lav = patient.last_chart_review_at
    if lav is None:
        return None
    rd = lav.date()
    n_reports = DiagnosticReport.objects.filter(patient=patient, created_at__gte=lav).count()
    n_obs = Observation.objects.filter(patient=patient, observed_at__gte=rd).count()
    n_notes = ClinicalNote.objects.filter(patient=patient, note_date__gte=rd).count()
    n_so = SourceBackedObservation.objects.filter(patient=patient, created_at__gte=lav).count()
    total = n_reports + n_obs + n_notes + n_so
    return {
        "reports_ingested": n_reports,
        "dated_observations": n_obs,
        "clinical_notes": n_notes,
        "source_flags_created": n_so,
        "total": total,
    }


def patient_queue_counts(patient: Patient) -> Dict[str, Any]:
    since = count_new_since_last_review(patient)
    return {
        "unreviewed_source_flags": SourceBackedObservation.objects.filter(
            patient=patient,
            reviewed=False,
        ).count(),
        "unconfirmed_observations": Observation.objects.filter(
            patient=patient,
            confirmation_status="unconfirmed",
        ).count(),
        "pending_reports": DiagnosticReport.objects.filter(
            patient=patient,
            parse_status__in=PARSE_NEEDS_QUEUE,
        ).count(),
        "new_since_last_review": since["total"] if since else None,
        "new_since_last_review_breakdown": since,
    }


def patient_in_review_queue(patient: Patient, *, now: Optional[datetime] = None) -> bool:
    """
    True if the chart should appear on the review queue for follow-up.
    """
    now = now or timezone.now()
    rs = normalized_review_status(patient)
    if rs in ("needs_review", "watch"):
        return True
    if Observation.objects.filter(patient=patient, confirmation_status="unconfirmed").exists():
        return True
    if SourceBackedObservation.objects.filter(patient=patient, reviewed=False).exists():
        return True
    if DiagnosticReport.objects.filter(patient=patient, parse_status__in=PARSE_NEEDS_QUEUE).exists():
        return True

    lav = patient.last_chart_review_at
    cutoff_21 = now - timedelta(days=21)

    if lav is not None:
        rd = lav.date()
        if DiagnosticReport.objects.filter(patient=patient, created_at__gte=lav).exists():
            return True
        if (
            Observation.objects.filter(patient=patient, observed_at__gte=rd)
            .exclude(confirmation_status="rejected")
            .exists()
        ):
            return True
        if ClinicalNote.objects.filter(patient=patient, note_date__gte=rd).exists():
            return True
        # New flags created since review (often overlap unreviewed check)
        if SourceBackedObservation.objects.filter(patient=patient, created_at__gte=lav).exists():
            return True
        return False

    # No explicit chart review logged — retain rolling ingestion signal
    return DiagnosticReport.objects.filter(patient=patient, created_at__gte=cutoff_21).exists()


def queue_sort_key(patient: Patient, counts: Dict[str, Any]) -> Tuple[int, int, str, str]:
    """Ascending sort: urgent first."""
    rs = normalized_review_status(patient)
    status_rank = {"needs_review": 0, "watch": 1, "stable": 3}.get(rs, 2)
    w = (
        counts["unreviewed_source_flags"] * 40
        + counts["unconfirmed_observations"] * 25
        + counts["pending_reports"] * 20
        + (counts.get("new_since_last_review") or 0) * 2
    )
    return status_rank, -w, patient.last_name or "", patient.first_name or ""


def annotate_queue_hints(patient: Patient) -> Tuple[List[str], Dict[str, Any]]:
    counts = patient_queue_counts(patient)
    reasons = []
    if counts["unreviewed_source_flags"]:
        reasons.append(f"{counts['unreviewed_source_flags']} unreviewed source-backed observation(s)")
    if counts["unconfirmed_observations"]:
        reasons.append(
            f"{counts['unconfirmed_observations']} extracted observation row(s) need confirmation",
        )
    if counts["pending_reports"]:
        reasons.append(f"{counts['pending_reports']} report(s) pending parse / confirmation pipeline")
    nslr = counts.get("new_since_last_review")
    if nslr is not None and nslr > 0:
        reasons.append(f"{nslr} new dated/ingested item(s) since last chart review")
    for so in SourceBackedObservation.objects.filter(patient=patient, reviewed=False).order_by("-pk")[:3]:
        reasons.append(so.title)
    out: List[str] = []
    seen = set()
    for r in reasons:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out[:8], counts
