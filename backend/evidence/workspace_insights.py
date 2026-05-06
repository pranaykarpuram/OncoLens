"""
Deterministic, source-grounded workspace insights — no LLM, no diagnosis or treatment recommendations.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from django.db.models import Max

from evidence.cancer_profiles import CancerProfile, get_cancer_profile
from evidence.models import Observation, SourceBackedObservation
from patients.models import ClinicalNote, Treatment
from reports.models import DiagnosticReport


def disclaim_short() -> str:
    return "Source-backed excerpts only; may warrant clinician review. Not a diagnosis or treatment recommendation."


def _infer_rule_kind(evidence_json: dict) -> str:
    if not evidence_json:
        return "other"
    rk = evidence_json.get("rule_kind")
    if isinstance(rk, str):
        return rk
    if evidence_json.get("marker"):
        return "marker_trend"
    if evidence_json.get("needle"):
        return "missing_data"
    if evidence_json.get("biomarkers"):
        return "biomarker_documentation"
    if evidence_json.get("primary_phrase"):
        return "imaging_language"
    if evidence_json.get("terms"):
        return "symptom_language"
    return "other"


def latest_chart_date(patient) -> date:
    """Latest documented activity date across chart rows (for trailing windows)."""
    cand: List[date] = []
    agg = DiagnosticReport.objects.filter(patient=patient).aggregate(
        mx=Max("report_date"),
        mc=Max("created_at__date"),
    )
    if agg["mx"]:
        cand.append(agg["mx"])
    if agg["mc"]:
        cand.append(agg["mc"])

    o_agg = Observation.objects.filter(patient=patient).aggregate(mx=Max("observed_at"))
    if o_agg["mx"]:
        cand.append(o_agg["mx"])

    n_agg = ClinicalNote.objects.filter(patient=patient).aggregate(mx=Max("note_date"))
    if n_agg["mx"]:
        cand.append(n_agg["mx"])

    t_agg = Treatment.objects.filter(patient=patient).aggregate(mx=Max("start_date"))
    if t_agg["mx"]:
        cand.append(t_agg["mx"])

    so_agg = SourceBackedObservation.objects.filter(patient=patient).aggregate(mc=Max("created_at__date"))
    if so_agg["mc"]:
        cand.append(so_agg["mc"])

    if not cand:
        return date.today()
    return max(cand)


def trailing_window_days() -> int:
    return 56


def build_what_changed_window(patient, reference_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Compute the clinical comparison window for “what changed”.
    Uses last_chart_review_at (calendar day onward) when set; otherwise rolling N-day window ending at chart-latest.
    """
    ref = _ref_date(patient, reference_date)
    lav = getattr(patient, "last_chart_review_at", None)
    if lav is not None:
        cutoff = lav.date()
        if cutoff > ref:
            cutoff = ref
        start_iso = lav.isoformat()
        label = "What changed since last chart review"
        mode = "since_review"
    else:
        cutoff = ref - timedelta(days=trailing_window_days())
        if cutoff > ref:
            cutoff = ref
        start_iso = cutoff.isoformat()
        label = "What changed recently"
        mode = "rolling"
    return {
        "start": start_iso,
        "end": ref.isoformat(),
        "label": label,
        "mode": mode,
        "cutoff_date": cutoff,
        "ref_date": ref,
    }


def serialize_what_changed_window_for_api(window: Dict[str, Any]) -> Dict[str, str]:
    return {
        "start": str(window["start"]),
        "end": str(window["end"]),
        "label": str(window["label"]),
        "mode": str(window["mode"]),
    }


def _so_touches_trailing_window(so: SourceBackedObservation, cutoff: date, ref: date) -> bool:
    for ei in so.evidence_items.all():
        if ei.evidence_date and cutoff <= ei.evidence_date <= ref:
            return True
    cd = so.created_at.date()
    return cutoff <= cd <= ref


def _ref_date(patient, reference_date: Optional[date]) -> date:
    return reference_date or latest_chart_date(patient)


def _append_bullet(
    out: List[Dict[str, Any]],
    text: str,
    sources: List[Dict[str, Any]],
    max_bullets: int = 5,
) -> None:
    text = text.strip()
    if not text or len(out) >= max_bullets:
        return
    out.append({"text": text, "sources": sources[:8]})


def build_what_changed_summary(
    patient,
    *,
    reference_date: Optional[date] = None,
    max_bullets: int = 5,
    calm_mode: Optional[bool] = None,
    window: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Concise bullets for activity in the trailing window ending at reference_date (chart-latest by default).
    Window start comes from Patient.last_chart_review_at when present; otherwise rolling 56-day fallback.
    """
    profile = get_cancer_profile(patient)
    w = window or build_what_changed_window(patient, reference_date)
    cutoff = w["cutoff_date"]
    ref = w["ref_date"]
    bullets: List[Dict[str, Any]] = []

    if calm_mode is None:
        rs = (getattr(patient, "review_status", "") or "").lower().replace("-", "_")
        if rs == "stable":
            calm_mode = True
        else:
            sos_n = SourceBackedObservation.objects.filter(patient=patient).count()
            rep_n = DiagnosticReport.objects.filter(patient=patient).count()
            calm_mode = rep_n <= 5 and sos_n <= 4

    # Reports in window
    reps = []
    for r in DiagnosticReport.objects.filter(patient=patient).order_by("-report_date"):
        rd = r.report_date or r.created_at.date()
        if cutoff <= rd <= ref:
            reps.append(r)
    if reps:
        labels = [f'{r.report_type}:{r.title[:48]}' for r in reps[:4]]
        _append_bullet(
            bullets,
            f"Documentation found {len(reps)} report(s) dated between {cutoff.isoformat()} and {ref.isoformat()} "
            f"({', '.join(labels[:3])}{'…' if len(reps) > 3 else ''}). Source-backed chart entries — may warrant clinician review.",
            [{"kind": "report", "label": r.title, "id": r.pk} for r in reps[:5]],
            max_bullets,
        )

    # Profile-aware tumor markers, biomarkers, and key labs in window
    profile_terms: List[str] = []
    for key in ("tumor_markers", "biomarkers", "labs"):
        profile_terms.extend(str(x) for x in (profile.get(key) or []) if x)
    obs_qs = Observation.objects.filter(
        patient=patient,
        observed_at__gte=cutoff,
        observed_at__lte=ref,
        confirmation_status="confirmed",
    ).order_by("-observed_at")
    marker_hits = []
    for o in obs_qs:
        if o.observation_type not in ("tumor_marker", "biomarker", "lab"):
            continue
        blob = f"{o.name} {o.value_text}".lower()
        if any(t.lower() in blob for t in profile_terms):
            marker_hits.append(o)
    if marker_hits:
        sample = ", ".join(f"{o.name} ({o.observed_at})" for o in marker_hits[:3])
        _append_bullet(
            bullets,
            f"Confirmed observations document profile-aligned marker, biomarker, or lab rows in this window: {sample}. "
            "Values are extracted from source documents only.",
            [{"kind": "observation", "label": o.name, "id": o.pk} for o in marker_hits[:5]],
            max_bullets,
        )

    # Profile-aware missing-data flags before imaging/symptoms so they are not truncated at max_bullets
    checks = profile.get("missing_data_checks") or []
    needles = [(c.get("observation_name_contains") or "").lower() for c in checks if c.get("observation_name_contains")]
    for so in SourceBackedObservation.objects.filter(patient=patient).prefetch_related("evidence_items"):
        if _infer_rule_kind(so.evidence_json or {}) != "missing_data":
            continue
        if not _so_touches_trailing_window(so, cutoff, ref):
            continue
        ej_needle = str((so.evidence_json or {}).get("needle", "")).lower()
        title_low = so.title.lower()
        if needles and any(n and (n in ej_needle or n in title_low) for n in needles):
            _append_bullet(
                bullets,
                f"A source-backed completeness heuristic flags a possible documentation gap ({so.title}). "
                "This is a chart-completeness signal only — may warrant clinician review.",
                [{"kind": "source_observation", "label": so.title, "id": so.pk}],
                max_bullets,
            )
            break

    # Imaging / imaging_language observations (+ MRI/PET wording in imaging reports when profile NET)
    img_obs = [o for o in obs_qs if o.observation_type == "imaging_language"]
    img_reports = [r for r in reps if getattr(r, "report_type", "") == "imaging"]
    imaging_vocab = [t.lower() for t in (profile.get("imaging_terms") or [])]
    extra_img = []
    for r in reps:
        blob = ((r.summary or "") + " " + (r.raw_text or "")).lower()
        if "mri" in blob or "magnetic resonance" in blob:
            extra_img.append(r)
        elif imaging_vocab and any(t in blob for t in imaging_vocab if len(t) > 4):
            extra_img.append(r)
    img_reports = list({*img_reports, *extra_img})
    if img_obs or img_reports:
        parts = []
        srcs = []
        for o in img_obs[:3]:
            parts.append(o.name or "Imaging language row")
            srcs.append({"kind": "observation", "label": o.name or "Imaging", "id": o.pk})
        for r in img_reports[:2]:
            parts.append(r.title)
            srcs.append({"kind": "report", "label": r.title, "id": r.pk})
        _append_bullet(
            bullets,
            "Imaging-associated language or imaging reports were documented in this period ("
            + "; ".join(parts[:4])
            + "). Wording is source-grounded; interpretation requires clinician review.",
            srcs,
            max_bullets,
        )

    # Symptoms in notes / symptom observations
    symptom_terms = [s.lower() for s in (profile.get("symptoms") or [])]
    sym_obs = [o for o in obs_qs if o.observation_type == "symptom"]
    sym_notes = []
    for n in ClinicalNote.objects.filter(patient=patient, note_date__gte=cutoff, note_date__lte=ref):
        low = (n.text or "").lower()
        matched_terms = symptom_terms and any(t in low for t in symptom_terms)
        if matched_terms:
            sym_notes.append(n)
    if sym_obs or sym_notes:
        lbls = [o.name for o in sym_obs[:2]]
        if sym_notes:
            lbls.append(f"Clinical note {sym_notes[0].note_date}")
        srcs = [{"kind": "observation", "label": o.name, "id": o.pk} for o in sym_obs[:4]]
        srcs.extend({"kind": "clinical_note", "label": f"Note {n.note_date}", "id": n.pk} for n in sym_notes[:3])
        _append_bullet(
            bullets,
            "Symptom-related documentation was found (" + "; ".join(lbls[:4]) + ") — excerpts only; may warrant clinician review.",
            srcs,
            max_bullets,
        )

    # Other source-backed observations tied to evidence dates in window (not creation time alone)
    flgs = []
    for so in (
        SourceBackedObservation.objects.filter(patient=patient)
        .prefetch_related("evidence_items")
        .order_by("-created_at")
    ):
        if _so_touches_trailing_window(so, cutoff, ref):
            flgs.append(so)
        if len(flgs) >= 6:
            break
    if flgs:
        titles = "; ".join(f.title for f in flgs[:3])
        _append_bullet(
            bullets,
            f"Source-backed observation flags surfaced: {titles}. Rules operate on extracted text — clinician review suggested.",
            [{"kind": "source_observation", "label": f.title, "id": f.pk} for f in flgs[:5]],
            max_bullets,
        )

    # Treatment line (lower priority than profile gaps / flags)
    txs = Treatment.objects.filter(patient=patient).filter(start_date__gte=cutoff - timedelta(days=400))
    txs = [t for t in txs if t.start_date and cutoff <= t.start_date <= ref]
    if not txs:
        txs = list(
            Treatment.objects.filter(patient=patient, start_date__lte=ref).order_by("-start_date")[:2]
        )
    if txs:
        t = txs[0]
        _append_bullet(
            bullets,
            f"Treatment documentation includes {t.name} (chart narrative as recorded). Source-backed administrative line — not a prescribing recommendation.",
            [{"kind": "treatment", "label": t.name, "id": t.pk}],
            max_bullets,
        )

    if len(bullets) < 2:
        n_obs = obs_qs.count()
        _append_bullet(
            bullets,
            f"Chart review window ({cutoff.isoformat()} – {ref.isoformat()}) contains {n_obs} dated observation row(s) "
            f"and {len(reps)} report(s). No additional highlight phrases matched — may still warrant routine clinician review.",
            [],
            max_bullets,
        )

    out = bullets[:max_bullets]
    if calm_mode and out:
        out[-1] = {
            **out[-1],
            "text": out[-1]["text"]
            + " Overall pattern is consistent with limited change in this demo excerpt set; clinical judgment remains primary.",
        }
    return out


def _theme_label(key: str) -> str:
    return {
        "marker_trend": "Tumor marker trend",
        "imaging_language": "Imaging language",
        "symptom_language": "Symptoms",
        "missing_data": "Missing data",
        "biomarker_documentation": "Biomarkers",
        "other": "Other findings",
    }.get(key, key.replace("_", " ").title())


def build_evidence_summary(
    patient,
    profile: Optional[CancerProfile] = None,
) -> Dict[str, Any]:
    """Themes from SourceBackedObservation + linked evidence items."""
    profile = profile or get_cancer_profile(patient)
    sos = list(
        SourceBackedObservation.objects.filter(patient=patient)
        .prefetch_related("evidence_items")
        .order_by("-created_at")
    )

    theme_counts: Dict[str, int] = {}
    source_ids: List[int] = []
    seen_ids = set()

    for so in sos:
        rk = _infer_rule_kind(so.evidence_json or {})
        theme_counts[rk] = theme_counts.get(rk, 0) + 1
        for ei in so.evidence_items.all():
            if ei.pk not in seen_ids:
                seen_ids.add(ei.pk)
                source_ids.append(ei.pk)

    themes_out = []
    for key, count in sorted(theme_counts.items(), key=lambda x: (-x[1], x[0])):
        themes_out.append({"key": key, "label": _theme_label(key), "count": count})

    profile_hits = []
    for label, terms in (
        ("Tumor markers", profile.get("tumor_markers") or []),
        ("Labs", profile.get("labs") or []),
        ("Biomarkers", profile.get("biomarkers") or []),
        ("Symptoms (vocabulary)", profile.get("symptoms") or []),
    ):
        if terms:
            profile_hits.append(f"{label}: {', '.join(str(t) for t in terms[:5])}")

    active_themes = []
    for key in ("marker_trend", "imaging_language", "symptom_language", "missing_data", "biomarker_documentation"):
        c = theme_counts.get(key, 0)
        if c:
            active_themes.append(f"{_theme_label(key)} ({c})")

    summary_parts = [
        f"Profile ({profile.get('id', 'general')}) emphasizes: " + "; ".join(profile_hits[:4]) if profile_hits else "",
    ]
    if active_themes:
        summary_parts.append("Source-backed rule themes currently represented: " + ", ".join(active_themes) + ".")
    if sos:
        summary_parts.append(
            f"{len(sos)} source-backed observation(s) are active in this chart with {len(source_ids)} linked evidence item(s)."
        )
    else:
        summary_parts.append("No source-backed observation flags are present yet for this chart.")

    summary_text = " ".join(p for p in summary_parts if p).strip()
    if not summary_text:
        summary_text = "Limited structured evidence flags; continue routine documentation review."

    return {
        "summary_text": summary_text + " " + disclaim_short(),
        "themes": themes_out,
        "source_count": len(source_ids),
        "source_ids": source_ids[:80],
        "profile_id": profile.get("id"),
    }


def build_missing_data_summary(patient, profile: Optional[CancerProfile] = None) -> str:
    profile = profile or get_cancer_profile(patient)
    checks = profile.get("missing_data_checks") or []
    parts = []
    for c in checks:
        needle = c.get("observation_name_contains") or ""
        days = int(c.get("window_days") or 30)
        if needle:
            parts.append(f"Completeness check: recent “{needle}” documentation within ~{days} days (heuristic).")
    so_missing = [
        so
        for so in SourceBackedObservation.objects.filter(patient=patient)
        if _infer_rule_kind(so.evidence_json or {}) == "missing_data"
    ]
    if so_missing:
        parts.append("Flags note possible chart gaps: " + "; ".join(so.title for so in so_missing[:4]) + ".")
    if not parts:
        return "No additional missing-data heuristics fired for this profile in the current rule set."
    return " ".join(parts) + " " + disclaim_short()
