from __future__ import annotations

from evidence.cancer_profiles import get_cancer_profile

from .models import SearchIndexEntry


def chunk_text(text: str, max_chars: int = 900, overlap: int = 150) -> list[str]:
    """Split text into overlapping windows for lexical + embedding indexing."""
    t = text or ""
    if not t.strip():
        return []
    chunks: list[str] = []
    n = len(t)
    step = max(1, max_chars - overlap)
    start = 0
    while start < n:
        chunk = t[start : start + max_chars]
        chunks.append(chunk)
        if len(chunk) < max_chars:
            break
        start += step
    return chunks


def _delete_entries(source_type: str, source_id: int):
    SearchIndexEntry.objects.filter(source_type=source_type, source_id=source_id).delete()


def _truncate(s: str, n: int = 8000) -> str:
    return s[:n] if len(s) > n else s


def index_report(report):
    """Index a DiagnosticReport for lexical search (chunked)."""
    from reports.models import DiagnosticReport

    assert isinstance(report, DiagnosticReport)
    _delete_entries("report", report.pk)
    title = (report.title or "").strip()
    body = report.raw_text or ""
    chunks = chunk_text(body)
    if not chunks:
        chunks = [title] if title else []
    if not chunks:
        return

    profile = get_cancer_profile(report.patient)
    rd = report.report_date or report.created_at.date()
    base_meta = {
        "report_type": report.report_type,
        "parse_status": report.parse_status,
        "source_date": rd.isoformat() if rd else None,
        "cancer_profile_id": profile.get("id"),
    }
    total = len(chunks)
    bulk: list[SearchIndexEntry] = []
    for i, ch in enumerate(chunks):
        if title:
            display_title = title if i == 0 else f"{title} · part {i + 1}"
            text_blob = f"{title}\n{ch}".strip()
        else:
            display_title = f"Report · part {i + 1}" if total > 1 else "Report"
            text_blob = ch.strip()
        meta = {**base_meta, "chunk_index": i, "chunk_total": total}
        bulk.append(
            SearchIndexEntry(
                patient=report.patient,
                source_type="report",
                source_id=report.pk,
                title=_truncate(display_title, 255),
                text=_truncate(text_blob),
                search_text=text_blob.lower(),
                metadata=meta,
            )
        )
    SearchIndexEntry.objects.bulk_create(bulk)


def index_clinical_note(note):
    from patients.models import ClinicalNote

    assert isinstance(note, ClinicalNote)
    _delete_entries("clinical_note", note.pk)
    title_prefix = note.get_note_type_display()
    patient_name = note.patient.full_name
    body = note.text or ""
    header = f"{title_prefix} {patient_name}".strip()
    chunks = chunk_text(body)
    if not chunks:
        chunks = [header] if header else []
    if not chunks:
        return

    nd = note.note_date
    base_meta = {
        "note_type": note.note_type,
        "source_date": nd.isoformat() if nd else None,
    }
    total = len(chunks)
    bulk: list[SearchIndexEntry] = []
    for i, ch in enumerate(chunks):
        text_blob = f"{header}\n{ch}".strip() if header else ch.strip()
        display_title = (
            f"{title_prefix} · {nd}" if i == 0 else f"{title_prefix} · {nd} · part {i + 1}"
        )
        meta = {**base_meta, "chunk_index": i, "chunk_total": total}
        bulk.append(
            SearchIndexEntry(
                patient=note.patient,
                source_type="clinical_note",
                source_id=note.pk,
                title=_truncate(display_title, 255),
                text=_truncate(text_blob),
                search_text=text_blob.lower(),
                metadata=meta,
            )
        )
    SearchIndexEntry.objects.bulk_create(bulk)


def index_observation(obs):
    from evidence.models import Observation

    assert isinstance(obs, Observation)
    _delete_entries("observation", obs.pk)
    parts = [obs.name, obs.value_text, obs.source_snippet or ""]
    blob = "\n".join(p for p in parts if p).strip()
    threshold = 900
    chunks = chunk_text(blob) if len(blob) > threshold else ([blob] if blob else [])
    if not chunks:
        return

    od = obs.observed_at
    base_meta = {
        "confirmation_status": obs.confirmation_status,
        "observation_type": obs.observation_type,
        "source_date": od.isoformat() if od else None,
    }
    total = len(chunks)
    bulk: list[SearchIndexEntry] = []
    for i, ch in enumerate(chunks):
        title = f"{obs.name} ({obs.get_observation_type_display()})"
        if total > 1:
            title = f"{title} · part {i + 1}"
        meta = {**base_meta, "chunk_index": i, "chunk_total": total}
        bulk.append(
            SearchIndexEntry(
                patient=obs.patient,
                source_type="observation",
                source_id=obs.pk,
                title=_truncate(title, 255),
                text=_truncate(ch),
                search_text=ch.lower(),
                metadata=meta,
            )
        )
    SearchIndexEntry.objects.bulk_create(bulk)


def index_evidence_item(item):
    from evidence.models import EvidenceItem

    assert isinstance(item, EvidenceItem)
    _delete_entries("evidence_item", item.pk)
    blob = f"{item.title}\n{item.snippet}".strip()
    threshold = 900
    chunks = chunk_text(blob) if len(blob) > threshold else ([blob] if blob else [])
    if not chunks:
        return

    ed = item.evidence_date
    base_meta = {"original_source_type": item.source_type, "source_date": ed.isoformat() if ed else None}
    total = len(chunks)
    bulk: list[SearchIndexEntry] = []
    for i, ch in enumerate(chunks):
        title = item.title if i == 0 else f"{item.title} · part {i + 1}"
        meta = {**base_meta, "chunk_index": i, "chunk_total": total}
        bulk.append(
            SearchIndexEntry(
                patient=item.patient,
                source_type="evidence_item",
                source_id=item.pk,
                title=_truncate(title, 255),
                text=_truncate(ch),
                search_text=ch.lower(),
                metadata=meta,
            )
        )
    SearchIndexEntry.objects.bulk_create(bulk)


def index_source_backed_observation(so):
    from evidence.models import SourceBackedObservation

    assert isinstance(so, SourceBackedObservation)
    _delete_entries("source_observation", so.pk)
    blob = "\n".join(
        p for p in (so.title, so.explanation, so.reason) if p
    ).strip()
    threshold = 900
    chunks = chunk_text(blob) if len(blob) > threshold else ([blob] if blob else [])
    if not chunks:
        return

    sd = so.created_at.date()
    base_meta = {"source_date": sd.isoformat()}
    total = len(chunks)
    bulk: list[SearchIndexEntry] = []
    for i, ch in enumerate(chunks):
        title = so.title if i == 0 else f"{so.title} · part {i + 1}"
        meta = {**base_meta, "chunk_index": i, "chunk_total": total}
        bulk.append(
            SearchIndexEntry(
                patient=so.patient,
                source_type="source_observation",
                source_id=so.pk,
                title=_truncate(title, 255),
                text=_truncate(ch),
                search_text=ch.lower(),
                metadata=meta,
            )
        )
    SearchIndexEntry.objects.bulk_create(bulk)


def reindex_patient(patient):
    """Rebuild search entries for everything tied to patient (simple full rebuild)."""
    SearchIndexEntry.objects.filter(patient=patient).delete()
    from evidence.models import EvidenceItem, Observation, SourceBackedObservation

    from reports.models import DiagnosticReport

    for r in DiagnosticReport.objects.filter(patient=patient):
        index_report(r)
    for n in patient.clinical_notes.all():
        index_clinical_note(n)
    for o in Observation.objects.filter(patient=patient):
        index_observation(o)
    for e in EvidenceItem.objects.filter(patient=patient):
        index_evidence_item(e)
    for so in SourceBackedObservation.objects.filter(patient=patient):
        index_source_backed_observation(so)


def reindex_all():
    """Rebuild SearchIndexEntry rows for every patient (embeddings cleared until rebuild_embeddings)."""
    from patients.models import Patient

    for patient in Patient.objects.iterator(chunk_size=50):
        reindex_patient(patient)
