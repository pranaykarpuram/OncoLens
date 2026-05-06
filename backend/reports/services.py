from __future__ import annotations

from django.db import transaction

from evidence.models import EvidenceItem, Observation
from evidence.services import generate_source_backed_observations
from reports.parsers import infer_date_from_text, parse_report_text


def normalize_marker_name(name: str) -> str:
    return name.lower().replace(" ", "").replace("ca199", "ca19-9").replace("ca-19-9", "ca19-9")


@transaction.atomic
def apply_parse_to_report(report, create_observations: bool = True) -> dict:
    """
    Parse report text into unconfirmed Observation and EvidenceItem rows.
    """
    parsed = parse_report_text(report)
    if create_observations:
        Observation.objects.filter(report=report, confirmation_status="unconfirmed").delete()
        EvidenceItem.objects.filter(metadata__report_id=report.pk).delete()

    observed_at = report.report_date
    if not observed_at and report.raw_text:
        observed_at = infer_date_from_text(report.raw_text)

    created_obs_ids = []

    def make_obs(obs_type: str, name: str, value_text: str = "", value_number=None, unit: str = "", snippet: str = "", conf: float = 1.0):
        o = Observation.objects.create(
            patient=report.patient,
            report=report,
            encounter=None,
            observation_type=obs_type,
            name=name,
            value_text=value_text[:255],
            value_number=value_number,
            unit=(unit or "")[:50],
            observed_at=observed_at,
            source_snippet=snippet,
            confidence=conf,
            confirmation_status="unconfirmed",
        )
        created_obs_ids.append(o.pk)
        EvidenceItem.objects.create(
            patient=report.patient,
            source_type="observation",
            source_id=o.pk,
            title=f"Extracted: {name}",
            snippet=snippet or value_text or name,
            evidence_date=observed_at,
            confidence=conf,
            metadata={
                "report_id": report.pk,
                "observation_id": o.pk,
                "kind": "extraction",
            },
        )

    total_extractions = 0
    for lab in parsed.get("labs", []):
        name = lab.get("name") or "Lab value"
        make_obs(
            "tumor_marker" if "CA 19" in name.upper() else "lab",
            name,
            value_text=str(lab["value_number"]) if lab.get("value_number") is not None else "",
            value_number=lab.get("value_number"),
            unit=lab.get("unit") or "",
            snippet=lab.get("snippet", ""),
            conf=float(lab.get("confidence") or 0.9),
        )
        total_extractions += 1

    for bio in parsed.get("biomarkers", []):
        make_obs(
            "biomarker",
            bio.get("name", "Biomarker"),
            value_text=bio.get("value_text", "")[:255],
            snippet=bio.get("snippet", ""),
            conf=float(bio.get("confidence") or 0.85),
        )
        total_extractions += 1

    for sym in parsed.get("symptoms", []):
        make_obs(
            "symptom",
            sym.get("name", "Symptom mention"),
            value_text="mentioned",
            snippet=sym.get("snippet", ""),
            conf=float(sym.get("confidence") or 0.8),
        )
        total_extractions += 1

    for img in parsed.get("imaging_language", []):
        make_obs(
            "imaging_language",
            img.get("name", "Imaging language"),
            value_text="language detected",
            snippet=img.get("snippet", ""),
            conf=float(img.get("confidence") or 0.81),
        )
        total_extractions += 1

    for tx in parsed.get("treatments", []):
        make_obs(
            "other",
            tx.get("name", "Treatment mention"),
            value_text="mentioned",
            snippet=tx.get("snippet", ""),
            conf=float(tx.get("confidence") or 0.8),
        )
        total_extractions += 1

    report.parse_status = "needs_confirmation" if total_extractions else "parsed"
    if not total_extractions:
        report.summary = report.summary or "No structured extractions detected; clinician review suggested."
    report.save(update_fields=["parse_status", "summary", "updated_at"])

    return {"parsed": parsed, "observation_ids": created_obs_ids, "extraction_count": total_extractions}


def confirm_extractions(report, user) -> None:
    """Confirm observations tied to report; preserves rows already marked rejected."""
    Observation.objects.filter(report=report).exclude(confirmation_status="rejected").update(
        confirmation_status="confirmed",
        confirmed_by=user,
    )
    report.parse_status = "parsed"
    report.save(update_fields=["parse_status", "updated_at"])
    generate_source_backed_observations(report.patient)


def reject_extractions(report) -> None:
    Observation.objects.filter(report=report).update(confirmation_status="rejected")
    report.parse_status = "parsed"
    report.save(update_fields=["parse_status", "updated_at"])
