"""Lexical + local semantic (embedding) evidence search."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Q
from django.urls import reverse

from evidence.cancer_profiles import get_cancer_profile, profile_vocabulary_flat
from evidence.models import EvidenceItem, Observation, SearchIndexEntry, SourceBackedObservation
from patients.models import ClinicalNote, Patient
from reports.models import DiagnosticReport

logger = logging.getLogger(__name__)

KNOWN_TERMS = ("kras", "folfirinox", "gemcitabine", "bilirubin", "paclitaxel", "radiation")

SEMANTIC_WEIGHT = 22.0


def _rank_hints(needle: str, title: str, body: str, patient_full_name: str) -> float:
    n = needle.strip().lower()
    tl = (title or "").lower()
    bl = (body or "").lower()
    score = 0.0
    words = [w for w in n.replace(",", " ").split() if len(w) > 2]

    if n:
        if n in tl:
            score += 5
        elif any(tl.startswith(pref) for pref in (n, n.capitalize())):
            score += 5
        if n in bl:
            score += 3
        score += min(bl.count(n), 8)

    for w in words:
        score += 2 if w in tl else 0
        score += 1 if w and w != n and w in bl else 0

    pfn = patient_full_name.lower().split()[0][:3]
    if len(pfn) >= 2 and pfn in bl:
        score += 5

    if n:
        for term in KNOWN_TERMS:
            if term in n and term in bl:
                score += 4

    return score


def _recent_boost(ref: Optional[date]) -> float:
    if not ref:
        return 0.0
    return 1.0 if abs((date.today() - ref).days) <= 30 else 0.0


def _patient_profile_boost(patient_pk: Optional[int], query_lower: str) -> float:
    """Boost rank when query overlaps cancer-profile vocabulary for scoped patient search."""
    if patient_pk is None or not query_lower:
        return 0.0
    try:
        pat = Patient.objects.get(pk=patient_pk)
    except Patient.DoesNotExist:
        return 0.0
    vocab = profile_vocabulary_flat(get_cancer_profile(pat))
    bonus = 0.0
    for term in vocab:
        if len(term) > 2 and term in query_lower:
            bonus += 4.0
    return min(bonus, 16.0)


def _urls(pat: Patient, source_kind: str, source_id: Optional[int]) -> Tuple[str, str]:
    workspace_url = reverse("patients:workspace", kwargs={"pk": pat.pk})
    source_url = ""
    if source_kind == "report" and source_id:
        source_url = reverse("reports:review_extraction", kwargs={"pk": source_id})
    return workspace_url, source_url


def _merge_key(row: Dict[str, Any]) -> Tuple[int, str, int, int]:
    sid = row.get("source_id")
    if sid is None:
        sid = -1
    ci = row.get("chunk_index")
    if ci is None:
        ci = -1
    return (row["patient"].pk, row.get("source_kind", ""), sid, ci)


def _merge_evidence_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[Tuple[int, str, int, int], Dict[str, Any]] = {}
    for row in rows:
        key = _merge_key(row)
        if key not in merged:
            merged[key] = row
            continue
        cur = merged[key]
        if row["rank_hint"] > cur["rank_hint"]:
            cur["rank_hint"] = row["rank_hint"]
            for fld in ("matched_snippet", "why_matched", "extracted_value", "confidence", "source_url"):
                if fld in row:
                    cur[fld] = row[fld]
        a = row.get("similarity_score")
        b = cur.get("similarity_score")
        if a is not None:
            cur["similarity_score"] = max(a, b) if b is not None else a
        ka = row.get("result_kind", "keyword")
        kb = cur.get("result_kind", "keyword")
        cur["result_kind"] = "hybrid" if ka != kb else ka
        sd_new = row.get("source_date")
        if sd_new and not cur.get("source_date"):
            cur["source_date"] = sd_new
    out = list(merged.values())
    out.sort(key=lambda r: float(r["rank_hint"]), reverse=True)
    return out


def search_evidence(query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    filters = filters or {}
    qp = filters.get("patient")
    top_k = filters.get("top_k", 250)
    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        top_k = 250
    top_k = max(1, min(top_k, 500))

    q = (query or "").strip()
    ql = q.lower()
    rows: List[Dict[str, Any]] = []

    if not ql:
        return []

    prof_boost = _patient_profile_boost(qp, ql)

    def push(pat: Patient, rk: float, bucket: Dict[str, Any], kind: str = "keyword"):
        rk = rk + bucket.get("_base", 0.0) + prof_boost
        row = {
            "patient": pat,
            "rank_hint": rk,
            "result_kind": kind,
            "similarity_score": bucket.get("similarity_score"),
            **{k: v for k, v in bucket.items() if not k.startswith("_")},
        }
        rows.append(row)

    for entry in SearchIndexEntry.objects.select_related("patient").filter(search_text__icontains=ql).order_by(
        "-pk"
    )[:200]:
        if qp and entry.patient_id != qp:
            continue
        pat = entry.patient
        body = entry.text or ""
        rk = (
            _rank_hints(ql, entry.title, body, pat.full_name)
            + _recent_boost(pat.last_updated.date())
            + 10
        )
        chunk_index = entry.metadata.get("chunk_index")
        if chunk_index is None:
            chunk_index = 0
        workspace_url, source_url = _urls(pat, entry.source_type, entry.source_id)
        push(
            pat,
            rk,
            {
                "source_kind": entry.source_type,
                "source_type": entry.source_type.replace("_", " ").title(),
                "source_id": entry.source_id,
                "chunk_index": chunk_index,
                "matched_snippet": (body[:400] + "…") if len(body) > 400 else body or entry.title,
                "extracted_value": entry.metadata.get("extracted_value", "") or "",
                "why_matched": "Matched indexed search_text",
                "confidence": round(min(rk / 40.0, 1.0), 4),
                "workspace_url": workspace_url,
                "source_url": source_url,
                "source_date": entry.metadata.get("source_date"),
            },
        )

    reps = DiagnosticReport.objects.select_related("patient").filter(raw_text__icontains=ql)[:100]
    for rep in reps:
        if qp and rep.patient_id != qp:
            continue
        pat = rep.patient
        body = rep.raw_text or ""
        rk = (
            _rank_hints(ql, rep.title, body, pat.full_name)
            + _recent_boost(rep.report_date or rep.created_at.date())
            + 14
        )
        rd = rep.report_date or rep.created_at.date()
        workspace_url, source_url = _urls(pat, "report", rep.pk)
        push(
            pat,
            rk,
            {
                "source_kind": "report",
                "source_type": dict(rep.REPORT_TYPES).get(rep.report_type, rep.report_type),
                "source_id": rep.pk,
                "chunk_index": 0,
                "matched_snippet": body[:420] + ("…" if len(body) > 420 else ""),
                "extracted_value": "",
                "why_matched": "Matched report raw_text",
                "confidence": round(min(rk / 44.0, 1.0), 4),
                "workspace_url": workspace_url,
                "source_url": source_url,
                "source_date": rd.isoformat() if rd else None,
            },
        )

    for note in ClinicalNote.objects.select_related("patient").filter(text__icontains=ql)[:120]:
        if qp and note.patient_id != qp:
            continue
        pat = note.patient
        body = note.text or ""
        rk = _rank_hints(ql, note.get_note_type_display(), body, pat.full_name) + _recent_boost(
            note.note_date
        ) + 12
        nd = note.note_date
        workspace_url, _ = _urls(pat, "clinical_note", note.pk)
        push(
            pat,
            rk,
            {
                "source_kind": "clinical_note",
                "source_type": "Clinical Note",
                "source_id": note.pk,
                "chunk_index": 0,
                "matched_snippet": body[:380] + ("…" if len(body) > 380 else ""),
                "extracted_value": "",
                "why_matched": "Matched clinical note text",
                "confidence": round(min(rk / 42.0, 1.0), 4),
                "workspace_url": workspace_url,
                "source_url": "",
                "source_date": nd.isoformat() if nd else None,
            },
        )

    obs_q = (
        Observation.objects.select_related("patient", "report")
        .filter(Q(name__icontains=ql) | Q(value_text__icontains=ql) | Q(source_snippet__icontains=ql))
        .order_by("-pk")[:150]
    )
    for obs in obs_q:
        if qp and obs.patient_id != qp:
            continue
        pat = obs.patient
        body = f"{obs.name} {obs.value_text} {obs.source_snippet}"
        rk = _rank_hints(ql, obs.name, body, pat.full_name) + _recent_boost(obs.observed_at)
        rk += {
            "confirmed": 6,
            "unconfirmed": 2,
            "rejected": 1,
        }.get(obs.confirmation_status, 1)
        workspace_url = reverse("patients:workspace", kwargs={"pk": pat.pk})
        source_url = ""
        if getattr(obs.report, "pk", None):
            source_url = reverse("reports:review_extraction", kwargs={"pk": obs.report.pk})
        push(
            pat,
            rk + 15,
            {
                "source_kind": "observation",
                "source_type": dict(obs.OBSERVATION_TYPES).get(obs.observation_type, obs.observation_type),
                "source_id": obs.pk,
                "chunk_index": 0,
                "matched_snippet": (obs.source_snippet or obs.name or "")[:400],
                "extracted_value": f"{obs.name}: {obs.value_text or obs.value_number or ''}".strip(),
                "why_matched": "Matched observation fields",
                "confidence": min(max(obs.confidence, 0), 1.0),
                "workspace_url": workspace_url,
                "source_url": source_url,
                "source_date": obs.observed_at.isoformat() if obs.observed_at else None,
            },
        )

    for item in EvidenceItem.objects.select_related("patient").filter(
        snippet__icontains=ql,
    ).order_by("-pk")[:150]:
        if qp and item.patient_id != qp:
            continue
        pat = item.patient
        body = f"{item.title} {item.snippet}"
        rk = _rank_hints(ql, item.title, body, pat.full_name) + _recent_boost(item.evidence_date) + 8
        ed = item.evidence_date
        workspace_url, _ = _urls(pat, "evidence_item", item.pk)
        push(
            pat,
            rk,
            {
                "source_kind": "evidence_item",
                "source_type": item.get_source_type_display(),
                "source_id": item.pk,
                "chunk_index": 0,
                "matched_snippet": item.snippet[:400],
                "extracted_value": item.title,
                "why_matched": "Matched evidence snippet/title",
                "confidence": min(max(item.confidence, 0), 1.0),
                "workspace_url": workspace_url,
                "source_url": "",
                "source_date": ed.isoformat() if ed else None,
            },
        )

    so_q = SourceBackedObservation.objects.select_related("patient").filter(
        Q(title__icontains=ql) | Q(explanation__icontains=ql) | Q(reason__icontains=ql)
    ).order_by("-pk")[:80]
    for so in so_q:
        if qp and so.patient_id != qp:
            continue
        pat = so.patient
        body = f"{so.title} {so.explanation} {so.reason}"
        rk = _rank_hints(ql, so.title, body, pat.full_name) + _recent_boost(so.created_at.date()) + 13
        sd = so.created_at.date()
        workspace_url, _ = _urls(pat, "source_observation", so.pk)
        push(
            pat,
            rk,
            {
                "source_kind": "source_observation",
                "source_type": "Source-backed observation",
                "source_id": so.pk,
                "chunk_index": 0,
                "matched_snippet": (so.explanation or so.title or "")[:400],
                "extracted_value": so.title,
                "why_matched": "Matched source-backed observation fields",
                "confidence": 0.78,
                "workspace_url": workspace_url,
                "source_url": "",
                "source_date": sd.isoformat() if sd else None,
            },
        )

    candidates: List[Any] = []
    try:
        from evidence.ai_embeddings import semantic_search_candidates

        candidates = semantic_search_candidates(q, patient_id=qp, top_k=min(100, max(top_k * 3, 50)))
    except Exception as exc:
        logger.warning("Semantic evidence branch disabled: %s", exc)

    for entry, sim in candidates:
        pat = entry.patient
        body = entry.text or ""
        ref_date = None
        sd_raw = entry.metadata.get("source_date")
        if sd_raw:
            try:
                ref_date = date.fromisoformat(sd_raw)
            except (TypeError, ValueError):
                ref_date = None
        rk = 10 + SEMANTIC_WEIGHT * float(sim) + _recent_boost(ref_date)
        chunk_index = entry.metadata.get("chunk_index")
        if chunk_index is None:
            chunk_index = 0
        workspace_url, source_url = _urls(pat, entry.source_type, entry.source_id)
        push(
            pat,
            rk,
            {
                "source_kind": entry.source_type,
                "source_type": entry.source_type.replace("_", " ").title(),
                "source_id": entry.source_id,
                "chunk_index": chunk_index,
                "matched_snippet": (body[:400] + "…") if len(body) > 400 else body or entry.title,
                "extracted_value": entry.metadata.get("extracted_value", "") or "",
                "why_matched": "Semantic match (cosine similarity)",
                "confidence": round(min(float(sim), 1.0), 4),
                "workspace_url": workspace_url,
                "source_url": source_url,
                "source_date": sd_raw,
                "similarity_score": round(float(sim), 6),
            },
            kind="semantic",
        )

    merged = _merge_evidence_rows(rows)
    return merged[:top_k]

