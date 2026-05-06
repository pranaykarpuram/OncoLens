from __future__ import annotations

import json
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from briefs.models import TumorBoardBrief
from briefs.services import disclaim, generate_tumor_board_brief
from core.chart_review import annotate_queue_hints, patient_in_review_queue, patient_queue_counts, queue_sort_key
from core.timeline import timeline_for_patient
from evidence.cancer_profiles import get_cancer_profile
from evidence.models import EvidenceItem, Observation, SourceBackedObservation
from evidence.workspace_insights import (
    build_evidence_summary,
    build_missing_data_summary,
    build_what_changed_summary,
    build_what_changed_window,
    serialize_what_changed_window_for_api,
)
from evidence.search import search_evidence
from patients.models import Patient
from reports.models import DiagnosticReport
from reports.parsers import parse_report_text
from reports.services import apply_parse_to_report


def _reject_unauthenticated(request):
    if request.user.is_authenticated:
        return None
    return JsonResponse({"detail": "Authentication required"}, status=401)


def serialize_obs(o: Observation):
    return {
        "id": o.pk,
        "observation_type": o.observation_type,
        "name": o.name,
        "value_text": o.value_text,
        "value_number": o.value_number,
        "unit": o.unit,
        "observed_at": o.observed_at.isoformat() if o.observed_at else None,
        "source_snippet": o.source_snippet,
        "confidence": o.confidence,
        "confirmation_status": o.confirmation_status,
        "report_id": o.report_id,
    }


def serialize_evidence_item_preview(item):
    return {
        "id": item.pk,
        "title": item.title,
        "snippet": item.snippet,
        "evidence_date": item.evidence_date.isoformat() if item.evidence_date else None,
        "source_type": item.source_type,
        "source_id": item.source_id,
        "confidence": item.confidence,
    }


def serialize_source_obs(so: SourceBackedObservation):
    linked = [serialize_evidence_item_preview(i) for i in so.evidence_items.all()]
    return {
        "id": so.pk,
        "title": so.title,
        "explanation": so.explanation,
        "status": so.status,
        "reason": so.reason,
        "reviewed": so.reviewed,
        "evidence_item_ids": list(so.evidence_items.values_list("pk", flat=True)),
        "linked_evidence_items": linked,
        "evidence_json": so.evidence_json,
        "created_at": so.created_at.isoformat(),
    }


def serialize_brief(brief: TumorBoardBrief):
    return {
        "id": brief.pk,
        "patient_id": brief.patient_id,
        "case_summary": brief.case_summary,
        "treatment_course": brief.treatment_course,
        "key_timeline_events": brief.key_timeline_events,
        "evidence_of_change": brief.evidence_of_change,
        "missing_or_unconfirmed_data": brief.missing_or_unconfirmed_data,
        "source_documents": brief.source_documents,
        "created_at": brief.created_at.isoformat(),
        "disclaimer": disclaim(),
    }


def api_patient_evidence(request, pk):
    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    patient = get_object_or_404(Patient, pk=pk)
    profile = get_cancer_profile(patient)

    observations = Observation.objects.filter(patient=patient).order_by("-observed_at", "-pk")
    source_obs = SourceBackedObservation.objects.filter(patient=patient).prefetch_related(
        "evidence_items",
    ).order_by("-created_at")

    wchg = build_what_changed_window(patient)
    payload = {
        "patient": {
            "id": patient.pk,
            "name": patient.full_name,
            "mrn": patient.medical_record_number,
            "review_status": patient.review_status,
            "primary_diagnosis": patient.primary_diagnosis,
            "cancer_stage": patient.cancer_stage,
            "last_chart_review_at": patient.last_chart_review_at.isoformat()
            if patient.last_chart_review_at
            else None,
            "disclaimer": disclaim(),
        },
        "observations": [serialize_obs(o) for o in observations],
        "source_backed_observations": [serialize_source_obs(s) for s in source_obs],
        "timeline": timeline_for_patient(patient),
        "what_changed_window": serialize_what_changed_window_for_api(wchg),
        "what_changed_summary": build_what_changed_summary(patient, window=wchg),
        "evidence_summary": build_evidence_summary(patient, profile=profile),
        "missing_data_summary": build_missing_data_summary(patient, profile=profile),
    }
    return JsonResponse(payload, safe=False)


@csrf_exempt
@require_POST
def api_patient_mark_reviewed(request, pk):
    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    patient = get_object_or_404(Patient, pk=pk)
    now = timezone.now()
    patient.last_chart_review_at = now
    patient.save()
    SourceBackedObservation.objects.filter(patient=patient).update(reviewed=True)
    EvidenceItem.objects.filter(patient=patient).update(reviewed=True)
    patient.refresh_from_db()
    return JsonResponse(
        {
            "ok": True,
            "patient": {
                "id": patient.pk,
                "name": patient.full_name,
                "mrn": patient.medical_record_number,
                "review_status": patient.review_status,
                "primary_diagnosis": patient.primary_diagnosis,
                "cancer_stage": patient.cancer_stage,
                "last_chart_review_at": patient.last_chart_review_at.isoformat(),
            },
        }
    )


def api_evidence_search(request):
    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    query = request.GET.get("q", "").strip()
    filters = {}
    pid = request.GET.get("patient")
    if pid and pid.isdigit():
        filters["patient"] = int(pid)
    top_k_raw = request.GET.get("top_k", "25")
    try:
        top_k = int(top_k_raw)
    except (TypeError, ValueError):
        top_k = 25
    filters["top_k"] = max(1, min(top_k, 100))
    hits = search_evidence(query, filters)

    suggested_terms: list[str] = []
    if pid and pid.isdigit():
        try:
            scoped = Patient.objects.get(pk=int(pid))
            suggested_terms = list(get_cancer_profile(scoped).get("search_seed_terms") or [])
        except Patient.DoesNotExist:
            suggested_terms = []

    stripped = []
    for row in hits:
        stripped.append(
            {
                "patient": {
                    "id": row["patient"].pk,
                    "name": row["patient"].full_name,
                    "mrn": row["patient"].medical_record_number,
                },
                "source_kind": row.get("source_kind"),
                "source_type": row.get("source_type"),
                "matched_snippet": row.get("matched_snippet"),
                "extracted_value": row.get("extracted_value"),
                "why_matched": row.get("why_matched"),
                "confidence": row.get("confidence"),
                "source_url": row.get("source_url"),
                "workspace_url": row.get("workspace_url"),
                "rank_hint": row.get("rank_hint"),
                "similarity_score": row.get("similarity_score"),
                "source_date": row.get("source_date"),
                "result_kind": row.get("result_kind"),
                "source_id": row.get("source_id"),
                "chunk_index": row.get("chunk_index"),
            }
        )

    payload = {
        "results": stripped,
        "q": query,
        "disclaimer": "Evidence retrieval excerpts for clinician review only.",
    }
    if suggested_terms:
        payload["suggested_terms"] = suggested_terms

    return JsonResponse(payload, safe=False)


def _queue_aggregate():
    """Review queue cohort with chart-review-aware prioritization."""
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

    flagged: list[Patient] = []
    for p in Patient.objects.all().order_by("pk"):
        if patient_in_review_queue(p):
            flagged.append(p)
    flagged.sort(key=lambda p: queue_sort_key(p, patient_queue_counts(p)))

    return {
        "new_reports_count": DiagnosticReport.objects.filter(created_at__gte=cutoff).count(),
        "needs_confirmation_count": Observation.objects.filter(confirmation_status="unconfirmed").count(),
        "patients_with_new_evidence_count": SourceBackedObservation.objects.filter(reviewed=False)
        .values("patient_id")
        .distinct()
        .count(),
        "patients_pending_chart_review": len(flagged),
        "missing_recent_labs_count": missing_recent_labs_count,
        "review_patients": flagged,
    }


def serialize_public_patient(p: Patient):
    obs = Observation.objects.filter(patient=p, observation_type="tumor_marker", name__icontains="CA 19").order_by(
        "-observed_at"
    ).first()
    last_ca = obs.value_number if obs and obs.value_number is not None else None

    status_map = {"needs_review": "needs-review", "watch": "watch", "stable": "stable"}
    counts = patient_queue_counts(p)
    return {
        "id": p.pk,
        "name": p.full_name,
        "mrn": p.medical_record_number,
        "age": p.age,
        "sex": p.sex,
        "diagnosis": p.primary_diagnosis,
        "stage": p.cancer_stage,
        "treatment": p.current_treatment,
        "status": status_map.get(p.review_status, p.review_status),
        "ca199": last_ca,
        "trend": "n/a",
        "biomarkers": "",
        "updated": p.last_updated.isoformat(),
        "last_chart_review_at": p.last_chart_review_at.isoformat() if p.last_chart_review_at else None,
        "queue_counts": {
            "unreviewed_source_flags": counts["unreviewed_source_flags"],
            "unconfirmed_observations": counts["unconfirmed_observations"],
            "pending_reports": counts["pending_reports"],
            "new_since_last_review": counts["new_since_last_review"],
        },
    }


def newest_evidence_preview(patient: Patient):
    rep = DiagnosticReport.objects.filter(patient=patient).order_by("-created_at").first()
    if not rep:
        return None
    return {"type": rep.get_report_type_display(), "title": rep.title}


@csrf_exempt
@require_POST
def api_auth_login(request):
    try:
        data = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        data = {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({"ok": False, "detail": "Invalid credentials"}, status=401)
    login(request, user)
    profile = getattr(user, "profile", None)
    role = getattr(profile, "role", None)
    return JsonResponse(
        {
            "ok": True,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role,
            "disclaimer": "Clinical review tooling — not autonomous decision support.",
        }
    )


@csrf_exempt
@require_POST
def api_auth_logout(request):
    logout(request)
    return JsonResponse({"ok": True})


def api_auth_session(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        role = getattr(profile, "role", None)
        return JsonResponse(
            {
                "authenticated": True,
                "username": request.user.username,
                "role": role,
                "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
            }
        )
    return JsonResponse({"authenticated": False})


def api_review_queue(request):
    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    data = _queue_aggregate()
    patients_out = []
    for p in data["review_patients"]:
        hints, _ = annotate_queue_hints(p)
        patients_out.append(
            {
                **serialize_public_patient(p),
                "reasons": hints,
                "newestEvidence": newest_evidence_preview(p),
            }
        )
    return JsonResponse(
        {
            "metrics": {
                "new_reports_count": data["new_reports_count"],
                "needs_confirmation_count": data["needs_confirmation_count"],
                "patients_with_new_evidence_count": data["patients_with_new_evidence_count"],
                "missing_recent_labs_count": data["missing_recent_labs_count"],
                "patients_pending_chart_review": data["patients_pending_chart_review"],
            },
            "patients": patients_out,
            "disclaimer": disclaim(),
        },
        safe=False,
    )


def api_patients_search(request):
    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    q = (request.GET.get("q") or "").strip()
    qs = Patient.objects.all()
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(medical_record_number__icontains=q)
            | Q(primary_diagnosis__icontains=q)
        )
    qs = qs.order_by("last_name", "first_name")[:250]
    return JsonResponse({"patients": [serialize_public_patient(p) for p in qs]}, safe=False)


@csrf_exempt
@require_POST
def api_report_intake_json(request):
    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    try:
        data = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)
    try:
        pid = int(data.get("patient"))
    except (TypeError, ValueError):
        return JsonResponse({"detail": "patient id required"}, status=400)
    patient = get_object_or_404(Patient, pk=pid)

    rt = data.get("report_type") or "other"
    if rt not in dict(DiagnosticReport.REPORT_TYPES):
        rt = "other"

    rd = data.get("report_date")
    rd_parsed = None
    if rd:
        parts = rd.split("-")
        if len(parts) == 3:
            from datetime import date as d

            try:
                rd_parsed = d(int(parts[0]), int(parts[1]), int(parts[2]))
            except ValueError:
                rd_parsed = None

    title = (data.get("title") or "").strip()
    label = dict(DiagnosticReport.REPORT_TYPES).get(rt)
    computed_title = title or (f"{label} — {patient.full_name}")

    raw = (data.get("raw_text") or "").strip()
    if not raw:
        return JsonResponse({"detail": "raw_text is required"}, status=400)

    report = DiagnosticReport.objects.create(
        patient=patient,
        report_type=rt,
        report_date=rd_parsed,
        title=computed_title,
        raw_text=raw,
        uploaded_by=request.user,
        parse_status="pending",
    )
    outcome = apply_parse_to_report(report, create_observations=True)
    return JsonResponse(
        {
            "report_id": report.pk,
            "parse_status": report.parse_status,
            "extraction_count": outcome.get("extraction_count", 0),
            "workspace_url_hint": _reverse_safe("patients:workspace", {"pk": patient.pk}),
            "review_extraction_url_hint": _reverse_safe("reports:review_extraction", {"pk": report.pk}),
            "parsed_preview_summary": getattr(report, "summary", ""),
        },
        safe=False,
    )


def _reverse_safe(name: str, kwargs: dict):
    from django.urls import reverse

    try:
        return reverse(name, kwargs=kwargs)
    except Exception:
        return ""


@csrf_exempt
def api_patient_brief(request, pk):
    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        brief = generate_tumor_board_brief(patient, user=request.user)
        return JsonResponse(
            {"brief": serialize_brief(brief), "patient_id": patient.pk, "disclaimer": disclaim()},
            safe=False,
        )
    if request.method == "GET":
        brief = TumorBoardBrief.objects.filter(patient=patient).order_by("-pk").first()
        if not brief:
            return JsonResponse({"patient_id": patient.pk, "brief": None})
        return JsonResponse({"patient_id": patient.pk, "brief": serialize_brief(brief)})
    return JsonResponse({"detail": "Method not allowed"}, status=405)


def api_admin_summary(request):
    from django.contrib.auth import get_user_model

    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    if getattr(getattr(request.user, "profile", None), "role", None) != "admin":
        return JsonResponse({"detail": "Admin role required"}, status=403)
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    User = get_user_model()
    payload = {
        "user_total": User.objects.count(),
        "patient_total": Patient.objects.count(),
        "reports_parsed": DiagnosticReport.objects.filter(parse_status="parsed").count(),
        "unconfirmed_extractions": Observation.objects.filter(confirmation_status="unconfirmed").count(),
        "active_observations": Observation.objects.filter(confirmation_status="confirmed").count(),
        "disclaimer": "Operational rollup for development only.",
    }
    return JsonResponse(payload)


@csrf_exempt
def api_report_extract(request, pk):
    resp = _reject_unauthenticated(request)
    if resp:
        return resp
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    report = get_object_or_404(DiagnosticReport, pk=pk)
    persist_qs = request.GET.get("persist", "").lower()
    persist = persist_qs in ("1", "true", "yes")
    if not persist and request.body:
        try:
            body = json.loads(request.body.decode() or "{}")
            persist = str(body.get("persist", "")).lower() in ("1", "true", "yes")
        except json.JSONDecodeError:
            pass

    if persist:
        outcome = apply_parse_to_report(report, create_observations=True)
        report.refresh_from_db()
        payload = {"persisted": True, **outcome, "parse_status": report.parse_status}
        payload["parsed"] = outcome.get("parsed", {})
        return JsonResponse(payload, safe=False)

    parsed_preview = parse_report_text(report)
    return JsonResponse({"persisted": False, "parsed": parsed_preview}, safe=False)
