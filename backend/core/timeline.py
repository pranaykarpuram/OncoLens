from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from patients.models import ClinicalNote, Encounter, Treatment
from reports.models import DiagnosticReport


def timeline_for_patient(patient) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []

    def push(d: date | None, kind: str, title: str, desc: str):
        if d is None:
            return
        events.append({"date": d.isoformat(), "type": kind, "title": title, "detail": desc})

    for enc in Encounter.objects.filter(patient=patient).order_by("-date")[:120]:
        push(enc.date, enc.encounter_type or "other", enc.get_encounter_type_display(), enc.summary or "")

    for tr in Treatment.objects.filter(patient=patient).order_by("-start_date")[:120]:
        push(tr.start_date, "treatment", tr.name, tr.notes or "")

    for rep in DiagnosticReport.objects.filter(patient=patient).order_by("-report_date")[:220]:
        push(rep.report_date or rep.created_at.date(), dict(rep.REPORT_TYPES).get(rep.report_type, "report").lower(), rep.title, "")

    for note in ClinicalNote.objects.filter(patient=patient).order_by("-note_date")[:220]:
        push(note.note_date, dict(note.NOTE_TYPES).get(note.note_type, "clinical_note").lower(), note.get_note_type_display(), (note.text or "")[:200])

    events.sort(key=lambda e: e["date"], reverse=True)
    return events
