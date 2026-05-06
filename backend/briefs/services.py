"""Deterministic tumor board brief generation."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from evidence.models import Observation, SourceBackedObservation
from patients.models import ClinicalNote, Treatment
from reports.models import DiagnosticReport

from core.timeline import timeline_for_patient


RULE_MARKER = "__rule__:"


def disclaim() -> str:
    return "Generated from source documents for clinician review. Not a diagnosis or treatment recommendation."


def collect_timeline_snapshots(patient) -> List[Dict[str, Any]]:
    return [
        {
            **item,
            "kind": item.get("type"),
            "disclaimer": disclaim(),
        }
        for item in timeline_for_patient(patient)[:220]
    ]


def summarize_missing_fields(patient) -> List[Dict[str, str]]:
    bullets = []
    if not Observation.objects.filter(patient=patient, name__icontains="bilirubin").exists():
        bullets.append("Bilirubin not present in extracted observation list — clinician review suggested.")

    pending = Observation.objects.filter(patient=patient, confirmation_status="unconfirmed").count()
    if pending:
        bullets.append(f"{pending} extracted observation rows still unconfirmed.")

    if DiagnosticReport.objects.filter(patient=patient, parse_status="needs_confirmation").exists():
        bullets.append("One or more reports await extraction confirmation.")

    if not bullets:
        bullets.append("No heuristic chart gaps surfaced — clinician review still recommended.")

    return [{"bullet": b, "disclaimer": disclaim()} for b in bullets]


def summarize_source_documents(patient) -> List[Dict[str, str]]:
    chunks = []
    for rep in DiagnosticReport.objects.filter(patient=patient).order_by("-report_date")[:40]:
        chunks.append(
            {
                "type": dict(rep.REPORT_TYPES).get(rep.report_type, rep.report_type),
                "title": rep.title,
                "report_date": (rep.report_date or rep.created_at.date()).isoformat(),
                "disclaimer": disclaim(),
            }
        )
    return chunks


def summarize_evidence_of_change(patient) -> List[Dict[str, Any]]:
    out = []
    for so in SourceBackedObservation.objects.filter(patient=patient).order_by("-created_at")[:20]:
        out.append(
            {
                "title": so.title,
                "status": so.status,
                "explanation_excerpt": (so.explanation or "")[:500],
                "reason_excerpt": (so.reason.replace(RULE_MARKER, "").strip()[:500]),
                "disclaimer": disclaim(),
            }
        )
    return out


def generate_tumor_board_brief(patient, user=None):
    from briefs.models import TumorBoardBrief

    age = getattr(patient, "age", None)
    sex_part = getattr(patient, "sex", "") or ""
    age_part = f"{age}y" if age is not None else ""
    demographics = " ".join(p for p in (age_part, sex_part.strip()) if p).strip()

    case_summary = (
        f"{patient.full_name} ({demographics}), MRN {patient.medical_record_number}. "
        f"Primary oncology context field reads: {(patient.primary_diagnosis or '').strip()} — "
        f"staging narrative: {(patient.cancer_stage or '').strip()} — "
        f"current treatment narrative: {(patient.current_treatment or '').strip()}."
        f"\n\n{disclaim()}"
    )

    treatment_chunks = []
    for tr in Treatment.objects.filter(patient=patient).order_by("-start_date")[:8]:
        line = " · ".join(
            filter(
                None,
                (
                    tr.name,
                    tr.start_date.isoformat() if tr.start_date else "",
                    tr.status.lower() if tr.status else "",
                ),
            )
        )
        treatment_chunks.append(line + ("\nNote excerpts: " + tr.notes[:220] + "…" if tr.notes and len(tr.notes) > 220 else (("\nNotes: " + tr.notes) if tr.notes else "")))

    treatment_course_text = ("\n".join(treatment_chunks) + f"\n\n{disclaim()}").strip()

    timeline = collect_timeline_snapshots(patient)[:25]
    evidence_of_change = summarize_evidence_of_change(patient)

    evidence_json = [
        {
            "title": chunk["title"],
            "status": chunk["status"],
            "explanation_excerpt": chunk.get("explanation_excerpt") or "",
            "disclaimer": chunk["disclaimer"],
        }
        for chunk in evidence_of_change
    ]

    brief = TumorBoardBrief.objects.create(
        patient=patient,
        generated_by=user,
        case_summary=case_summary,
        treatment_course=treatment_course_text,
        key_timeline_events=[{k: v for k, v in ev.items()} for ev in timeline],
        evidence_of_change=evidence_json,
        missing_or_unconfirmed_data=summarize_missing_fields(patient),
        source_documents=summarize_source_documents(patient),
    )
    return brief
