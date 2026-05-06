from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from evidence.models import Observation, SourceBackedObservation
from patients.models import Patient
from reports.models import DiagnosticReport

from core.decorators import role_required


@login_required
def review_queue(request):
    now = timezone.now()
    cutoff = now - timedelta(days=21)
    cutoff_lab_date = timezone.now().date() - timedelta(days=30)

    reviewed_bili_pts = Observation.objects.filter(
        name__icontains="bilirubin",
        observed_at__gte=cutoff_lab_date,
        confirmation_status="confirmed",
    ).values_list("patient_id", flat=True)

    missing_recent_labs_count = (
        Patient.objects.exclude(current_treatment="")
        .exclude(pk__in=reviewed_bili_pts)
        .count()
    )

    review_patients = (
        Patient.objects.filter(
            Q(review_status__in=["needs_review", "watch"])
            | Q(observations__confirmation_status="unconfirmed")
            | Q(source_observations__reviewed=False)
            | Q(source_observations__status="needs_review")
            | Q(reports__created_at__gte=cutoff)
        )
        .distinct()
        .order_by("review_status", "last_updated")
    )

    new_reports_count = DiagnosticReport.objects.filter(created_at__gte=cutoff).count()
    needs_confirmation_count = Observation.objects.filter(confirmation_status="unconfirmed").count()
    patients_with_new_evidence_count = SourceBackedObservation.objects.filter(reviewed=False).values(
        "patient_id"
    ).distinct().count()

    context = {
        "review_patients": review_patients,
        "new_reports_count": new_reports_count,
        "needs_confirmation_count": needs_confirmation_count,
        "patients_with_new_evidence_count": patients_with_new_evidence_count,
        "missing_recent_labs_count": missing_recent_labs_count,
        "recent_cutoff": cutoff,
        "today": timezone.now().date(),
    }
    return render(request, "core/review_queue.html", context)


User = get_user_model()


@login_required
@role_required("admin")
def operations_dashboard(request):
    """Lightweight operations surface for admins only."""

    context = {
        "user_total": User.objects.count(),
        "patient_total": Patient.objects.count(),
        "reports_parsed": DiagnosticReport.objects.filter(parse_status="parsed").count(),
        "unconfirmed_extractions": Observation.objects.filter(confirmation_status="unconfirmed").count(),
        "active_observations": Observation.objects.filter(confirmation_status="confirmed").count(),
    }
    return render(request, "admin_panel/index.html", context)
