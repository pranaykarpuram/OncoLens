# OncoLens — Product scope (INFO 490)

## Problem

Oncology evidence is dispersed across unstructured documents and discrete data fields. OncoLens narrows review time by **gathering**, **prioritizing**, and **tracing** excerpts back to concrete chart sources—not by replacing clinician judgment.

## Users

- **MDs / APPs:** Review queue priority, workspace evidence board, search, tumor board prep.
- **Nurses / navigators:** Triage queues, symptom/marker wording, chart completeness hints.
- **Admin / ops:** Demo admin summary dashboard; staffing roles via `accounts.UserProfile`.

## In-scope features (build phase)

| Area | Description |
|------|-------------|
| Auth | Django session login; SPA `credentials: include` |
| Queue | Aggregate metrics + patient cards; chart-review-aware ordering |
| Workspace | Timeline, Evidence Board (grouped statuses), Source Viewer, “What changed”, evidence summary, chart search, Mark reviewed timestamp |
| Search | Hybrid lexical + local semantic embeddings + profile boost |
| Intake | Text-oriented report ingestion, parse, confirm/reject pathway |
| Briefs | Deterministic tumor board brief JSON + normalized React rendering |
| Data | Synthetic multi-tumor `seed_demo_data` corpus |

## Explicitly deprioritized

EHR FHIR feeds, billing/scheduling, patient-facing portal, autonomous treatment/diagnosis, production HIPAA posture, OCR on binary PDF pipelines (workflow is oriented to extractable/text paths in the prototype).

## User flow

```text
Login → Review Queue → Patient Workspace
         ↘ Evidence Search panel-wide
         
Workspace: What changed → Evidence Board → open card / chart search hit → Source Viewer
           → optionally Intake or Tumor Board → Mark reviewed when done
```

## System sketch

```text
[Django REST-style JSON APIs] ← session auth ← [React SPA :5173]
        ↑
SQLite ORM ← seed_demo ← parsers / rules ← (optional) semantic index rebuild
```

**AI boundary:** embeddings assist **retrieval rank** only; summaries and tumor board text assemble from deterministic rules/templates unless future work replaces them.
