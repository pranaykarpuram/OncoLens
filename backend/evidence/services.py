"""
Rule-based source-backed observations. Evidence-first language only — no diagnosis or therapy recommendation.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable, List, Set

from django.db import transaction

from evidence.cancer_profiles import CancerProfile, get_cancer_profile
from patients.models import ClinicalNote
from evidence.models import EvidenceItem, Observation, SourceBackedObservation

RULE_PREFIX = "__rule__:"


def _disclaimer() -> str:
    return (
        "Generated from source documents for clinician review. Not a diagnosis or treatment recommendation."
    )


def normalize_marker(name: str) -> str:
    n = (name or "").lower().replace(" ", "").replace("-", "")
    n = n.replace("ca199", "ca199").replace("ca19", "ca19")
    return n


def is_ca199_name(name: str) -> bool:
    return "ca19" in normalize_marker(name) or "ca199" in normalize_marker(name)


def _obs_matches_tumor_marker_family(obs_name: str, family: str) -> bool:
    n = (obs_name or "").lower()
    nm = normalize_marker(obs_name)
    if family == "ca199":
        return is_ca199_name(obs_name)
    if family == "chromogranin":
        return "chromogranin" in n or "cga" in nm or "chromogranin" in nm
    if family == "cea":
        return n.strip() == "cea" or n.startswith("cea ") or nm == "cea"
    if family == "ca153":
        return "15-3" in n or "ca15" in nm or "ca153" in nm
    return False


def _tumor_marker_families_for_profile(profile: CancerProfile) -> List[str]:
    """Dedupe logical families implied by profile tumor_markers labels."""
    families: List[str] = []
    for raw in profile["tumor_markers"]:
        ml = raw.lower()
        if "chromogranin" in ml or ml.strip() == "cga":
            if "chromogranin" not in families:
                families.append("chromogranin")
        elif "cea" in ml and "ca15" not in ml.replace(" ", "") and "ca 15" not in ml:
            if "cea" not in families:
                families.append("cea")
        elif "15-3" in ml or "ca15" in ml.replace(" ", "") or "ca 15" in ml.lower():
            if "ca153" not in families:
                families.append("ca153")
        elif "19" in ml or "ca19" in ml.replace(" ", "").lower():
            if "ca199" not in families:
                families.append("ca199")
    return families


def _display_name_for_family(family: str) -> str:
    return {
        "ca199": "CA 19-9",
        "chromogranin": "Chromogranin A",
        "cea": "CEA",
        "ca153": "CA 15-3",
    }.get(family, family)


def clear_rule_generated(patient):
    SourceBackedObservation.objects.filter(
        patient=patient,
        reviewed=False,
        reason__startswith=RULE_PREFIX,
    ).delete()


def _attach_items(obs: SourceBackedObservation, items: Iterable[EvidenceItem]):
    obs.evidence_items.add(*list(items))


@transaction.atomic
def generate_source_backed_observations(patient) -> List[SourceBackedObservation]:
    profile = get_cancer_profile(patient)
    clear_rule_generated(patient)
    created: List[SourceBackedObservation] = []
    created.extend(_rule_consecutive_marker_trend(patient, profile))
    created.extend(_rule_symptom_language(patient, profile))
    created.extend(_rule_imaging_language(patient, profile))
    created.extend(_rule_missing_data_checks(patient, profile))
    created.extend(_rule_biomarker_documentation(patient, profile))

    revisit = Observation.objects.filter(
        patient=patient,
        confirmation_status="unconfirmed",
    ).exists()
    reports_pending = patient.reports.filter(parse_status="needs_confirmation").exists()

    has_nr = revisit or reports_pending or SourceBackedObservation.objects.filter(
        patient=patient, reviewed=False, status="needs_review"
    ).exists()
    has_watch = (not has_nr) and SourceBackedObservation.objects.filter(
        patient=patient, reviewed=False, status="watch"
    ).exists()

    if has_nr:
        patient.review_status = "needs_review"
    elif has_watch:
        patient.review_status = "watch"
    else:
        patient.review_status = "stable"

    patient.save(update_fields=["review_status", "last_updated"])
    return created


def _rule_consecutive_marker_trend(patient, profile: CancerProfile) -> List[SourceBackedObservation]:
    out: List[SourceBackedObservation] = []
    for family in _tumor_marker_families_for_profile(profile):
        qs = Observation.objects.filter(
            patient=patient,
            observation_type__in=("tumor_marker", "lab"),
            confirmation_status="confirmed",
            value_number__isnull=False,
        )
        markers = sorted(
            [o for o in qs if _obs_matches_tumor_marker_family(o.name or "", family)],
            key=lambda o: (o.observed_at or date.min, o.pk),
        )
        if len(markers) < 3:
            continue

        # Longest strictly increasing run ending at the latest measurement (by date order).
        n = len(markers)
        run_end = n - 1
        run_start = n - 1
        while run_start > 0 and (markers[run_start - 1].value_number or 0) < (markers[run_start].value_number or 0):
            run_start -= 1
        run = markers[run_start:]
        if len(run) < 3:
            continue

        disp = _display_name_for_family(family)
        unit = (run[-1].unit or "").strip()
        parts = [f"{o.value_number:g}" + (f" {unit}" if unit else "") for o in run]
        data_points = " → ".join(parts)
        vals_csv = ", ".join(parts)
        ev_items = EvidenceItem.objects.filter(
            patient=patient,
            source_type="observation",
            source_id__in=[o.pk for o in run],
        )

        count = len(run)
        so = SourceBackedObservation.objects.create(
            patient=patient,
            title=f"{disp} has increased across {count} recent measurements",
            explanation=(
                f"Consecutive confirmed increases for {disp} were extracted from recent lab documentation. "
                "Evidence found in source documents — may warrant clinician review. "
                "Not a diagnosis or treatment recommendation."
            ),
            status="needs_review",
            reason=(
                f"{RULE_PREFIX}marker_trend_{family} "
                f"Flagged because {disp} rose across {count} consecutive measurements (strictly increasing)."
            ),
            evidence_json={
                "rule_kind": "marker_trend",
                "marker": disp,
                "values": vals_csv,
                "data_points": data_points,
                "measurement_count": count,
                "series_values": [float(o.value_number) for o in run if o.value_number is not None],
                "disclaimer": _disclaimer(),
            },
        )
        if ev_items.exists():
            _attach_items(so, ev_items)
        out.append(so)
    return out


def _recent_chart_text_lower(patient, days=120) -> str:
    cutoff = date.today() - timedelta(days=days)
    parts = []
    for n in ClinicalNote.objects.filter(patient=patient, note_date__gte=cutoff):
        parts.append((n.note_date, n.text or ""))
    for r in patient.reports.all():
        rd = r.report_date or r.created_at.date()
        if rd >= cutoff:
            parts.append((rd, r.raw_text or ""))
    parts.sort(key=lambda x: x[0], reverse=True)
    return "\n".join(text for _, text in parts).lower()


def _rule_symptom_language(patient, profile: CancerProfile) -> List[SourceBackedObservation]:
    hay = _recent_chart_text_lower(patient)
    needle_terms: List[str] = list(profile.get("symptoms") or [])
    for extra in ("fatigue", "pain", "nausea"):
        if extra not in needle_terms:
            needle_terms.append(extra)

    matched_terms = []
    for term in needle_terms:
        if term.lower() in hay:
            matched_terms.append(term)

    symptom_obs = Observation.objects.filter(
        patient=patient,
        observation_type="symptom",
        confirmation_status="confirmed",
    ).exists()

    if not matched_terms and not symptom_obs:
        return []

    if matched_terms:
        shown = matched_terms[:4]
        if len(shown) == 1:
            sym_title = f"Recent note documents {shown[0]}"
        else:
            sym_title = "Recent note documents " + ", ".join(shown[:-1]) + " and " + shown[-1]
    else:
        sym_title = "Recent note documents symptom-related language"

    so = SourceBackedObservation.objects.create(
        patient=patient,
        title=sym_title,
        explanation=(
            "Symptom-related language was identified in recent chart text (extracted excerpts only). "
            "Source-backed observation — may warrant clinician review."
        ),
        status="watch",
        reason=(
            f"{RULE_PREFIX}symptom_keywords "
            + (
                ", ".join(matched_terms)
                if matched_terms
                else "Confirmed symptom-category observation exists"
            )
        ),
        evidence_json={
            "rule_kind": "symptom_language",
            "terms": matched_terms,
            "primary_symptoms": matched_terms[:6],
            "disclaimer": _disclaimer(),
        },
    )
    qs = EvidenceItem.objects.filter(patient=patient).order_by("-pk")[:12]
    if qs.exists():
        _attach_items(so, qs)
    return [so]


def _rule_imaging_language(patient, profile: CancerProfile) -> List[SourceBackedObservation]:
    snippet_texts = []
    for o in Observation.objects.filter(
        patient=patient,
        observation_type="imaging_language",
        confirmation_status="confirmed",
    ):
        snippet_texts.append((o.source_snippet or o.name or "").lower())

    hay_reports = "".join((r.raw_text or "").lower() for r in patient.reports.all())
    hay = hay_reports + "\n" + "\n".join(snippet_texts) + "\n" + _recent_chart_text_lower(patient)

    terms_profile = [t.lower() for t in (profile.get("imaging_terms") or [])]
    base_terms = [
        "interval increase",
        "increased lesion size",
        "progression",
        "new lesion",
        "metastatic disease",
        "worsening",
        "suspicious for",
        "concerning for",
    ]
    all_terms: List[str] = []
    seen: Set[str] = set()
    for t in terms_profile + base_terms:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            all_terms.append(t)

    matched = [term for term in all_terms if term in hay]
    if not matched:
        return []

    # Prefer a concrete phrase for UI when present in chart-style language.
    phrase_candidates = [
        t for t in matched if " " in t or len(t) > 14
    ]
    primary_phrase = phrase_candidates[0] if phrase_candidates else matched[0]

    so = SourceBackedObservation.objects.create(
        patient=patient,
        title="Imaging report contains interval-change language",
        explanation=(
            "Imaging-associated wording appears in source documents (excerpts only). "
            "Evidence found — does not establish progression; may warrant clinician review."
        ),
        status="needs_review",
        reason=f"{RULE_PREFIX}imaging_language Matched excerpts: " + ", ".join(matched[:12]),
        evidence_json={
            "rule_kind": "imaging_language",
            "terms": matched,
            "primary_phrase": primary_phrase,
            "disclaimer": _disclaimer(),
        },
    )
    imgs = EvidenceItem.objects.filter(patient=patient, title__icontains="Imag")[:8]
    if not imgs.exists():
        imgs = EvidenceItem.objects.filter(patient=patient, title__icontains="CT")[:8]
    if not imgs.exists():
        imgs = EvidenceItem.objects.filter(patient=patient, title__icontains="MRI")[:8]
    if imgs.exists():
        _attach_items(so, imgs)

    imgs = EvidenceItem.objects.filter(patient=patient, title__startswith="Extracted").order_by("-pk")[:8]
    obs_items = EvidenceItem.objects.filter(patient=patient, title__icontains="language").order_by("-pk")[:6]
    for batch in (imgs, obs_items):
        if batch.exists():
            _attach_items(so, batch)
    return [so]


def _rule_missing_data_checks(patient, profile: CancerProfile) -> List[SourceBackedObservation]:
    out: List[SourceBackedObservation] = []
    for check in profile.get("missing_data_checks") or []:
        needle = check.get("observation_name_contains") or ""
        window = int(check.get("window_days") or 30)
        req_tx = bool(check.get("requires_active_treatment"))
        if req_tx and not (patient.current_treatment or "").strip():
            continue

        cutoff = date.today() - timedelta(days=window)
        has_recent = Observation.objects.filter(
            patient=patient,
            confirmation_status="confirmed",
            name__icontains=needle,
            observed_at__gte=cutoff,
        ).exists()
        if has_recent:
            continue

        needle_display = (needle or "lab").strip()
        title = f"No recent {needle_display} result found"

        so = SourceBackedObservation.objects.create(
            patient=patient,
            title=title,
            explanation=(
                f"No confirmed {needle_display} observation was found in the last {window} days "
                "(chart completeness hint only). Extracted from source documentation patterns — "
                "may warrant clinician review."
            ),
            status="watch",
            reason=(
                f"{RULE_PREFIX}missing_lab:{needle} "
                f"No matching observation in last {window} days."
            ),
            evidence_json={
                "rule_kind": "missing_data",
                "needle": needle,
                "window_days": window,
                "disclaimer": _disclaimer(),
            },
        )
        qs = EvidenceItem.objects.filter(patient=patient).order_by("-pk")[:6]
        if qs.exists():
            _attach_items(so, qs)
        out.append(so)
    return out


def _rule_biomarker_documentation(patient, profile: CancerProfile) -> List[SourceBackedObservation]:
    found: List[str] = []
    biomarkers = profile.get("biomarkers") or []

    for o in Observation.objects.filter(patient=patient, confirmation_status="confirmed"):
        blob = f"{o.name} {o.value_text} {o.source_snippet}".lower()
        for bio in biomarkers:
            if bio.lower() in blob and bio not in found:
                found.append(bio)

    for item in EvidenceItem.objects.filter(patient=patient):
        sn = (item.snippet or "").lower()
        for bio in biomarkers:
            if bio.lower() in sn and bio not in found:
                found.append(bio)

    for r in patient.reports.all():
        rt = (r.raw_text or "").lower()
        for bio in biomarkers:
            if bio.lower() in rt and bio not in found:
                found.append(bio)

    if not found:
        return []

    primary = found[0]

    so = SourceBackedObservation.objects.create(
        patient=patient,
        title=f"{primary} biomarker mention found",
        explanation=(
            f"Documentation includes references to {primary} (and possibly related terms) extracted for review. "
            "Source-backed observation — not a determination of mutation status or therapy selection."
        ),
        status="info",
        reason=f"{RULE_PREFIX}biomarker_terms Terms surfaced: " + ", ".join(found[:8]),
        evidence_json={
            "rule_kind": "biomarker_documentation",
            "biomarkers": found[:8],
            "primary_biomarker": primary,
            "disclaimer": _disclaimer(),
        },
    )
    qs = EvidenceItem.objects.filter(patient=patient).order_by("-pk")[:10]
    if qs.exists():
        _attach_items(so, qs)
    return [so]
