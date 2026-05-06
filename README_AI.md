# OncoLens — AI & retrieval documentation

This document describes **what is ML-based** versus **rule-based** in the current codebase, how to run indexing, and design tradeoffs. It matches the implementation under `backend/evidence/` and `backend/reports/parsers.py`.

## What is “AI” here?

| Component | Technique | Typical role |
|-----------|-----------|----------------|
| **Evidence search (semantic)** | `sentence_transformers.SentenceTransformer` — default `sentence-transformers/all-MiniLM-L6-v2`, overridable via `ONCOLENS_EMBEDDING_MODEL` | Ranks existing indexed **chunks** by cosine similarity to the query embedding |
| **Evidence search (lexical)** | `icontains` / heuristic rank (`evidence/search.py`) | Keyword matches on `SearchIndexEntry`, reports, notes, observations, evidence items, source-backed observations |
| **Profile boost** | Cancer vocabulary overlap (`evidence/cancer_profiles.py`) | Adds score when scoped patient matches profile terms |
| **Source-backed observations** | Deterministic Python rules (`evidence/services.py`) | Trends, imaging phrases, symptoms, missing-lab hints — **no** generative LM |
| **Report extraction** | Rule/regex parsers (`reports/parsers.py`) | Structured buckets from pasted text → **unconfirmed** rows until review |
| **Workspace “What changed” / summaries** | `evidence/workspace_insights.py` | Deterministic bullets from dated chart rows + profiles + review window (**no LLM**) |
| **Tumor board brief** | `briefs/services.py` — template-style assembly | **No** GPT; JSON stored on `TumorBoardBrief` |

There is **no** full RAG pipeline to an external chat model in this repo. Semantic search is **retrieve-only** over pre-indexed snippets.

---

## AI workflow (end-to-end)

1. **Load demo corpus** — `python manage.py seed_demo_data` creates patients, reports, observations, notes, treatments, briefs scaffolding, etc.
2. **Build lexical chunks** — `python manage.py rebuild_embeddings --reindex-first` rebuilds `SearchIndexEntry` rows (`evidence/search_index.py`).
3. **Compute embeddings** — same command invokes `evidence.ai_embeddings.rebuild_all_search_embeddings`, filling `SearchIndexEntry.embedding` (JSON vector).
4. **User query** — React calls `GET /api/evidence/search/?q=…&patient=<optional>` (`core/api_views.api_evidence_search` → `evidence.search.search_evidence`).
5. **Fusion** — Lexical rows + semantic candidates (`semantic_search_candidates`) merge in `_merge_evidence_rows`; **`result_kind`** becomes `keyword`, `semantic`, or `hybrid`.
6. **UI** — `SearchScreen` / `PatientWorkspaceScreen` render snippets, similarity, pills, workspace links; **Source Viewer** shows linked evidence trails.

Without step 2–3, search still returns **keyword** hits; semantic branch may be empty or degraded.

---

## Model selection

**Default:** `sentence-transformers/all-MiniLM-L6-v2` (set in `evidence/ai_embeddings.py`).  
**Why:** Public weights, modest size, sentence-level embeddings suitable for short clinical snippets; runs locally without paid API keys; reproducible with pinned dependencies.

---

## Indexed data (`SearchIndexEntry`)

The reindex pipeline materializes searchable rows from chart objects (reports chunked, snippets from observations/evidence/source-backed text, notes, etc. — see `evidence/search_index.py`). Fields used for retrieval include `search_text`, `text`, `metadata` (chunk index, dates, extracted hints).

---

## Search fusion (`evidence/search.py`)

- Lexical passages from multiple tables + `SearchIndexEntry`.
- `SEMANTIC_WEIGHT` scales embedding similarity contribution.
- Scoped search (`patient=` query param) filters candidates to one chart for workspace use.
- Suggested seeds from `get_cancer_profile(patient).search_seed_terms` are returned alongside results when scoped.

---

## Cancer-aware analysis

`evidence/cancer_profiles.py` defines profiles (pancreatic ADC/NET, colorectal, lung, breast, general). Each lists markers, biomarkers, labs, treatments, symptom vocabulary, imaging terms, and optional missing-data checks consumed by **`generate_source_backed_observations`** in `evidence/services.py`.

---

## Guardrails

- Retrieval returns **existing** text; embeddings do not authorize new clinical assertions.
- Disclaimers on API payloads / briefs: not diagnosis or treatment recommendation.
- Extracted labs/markers typically require **confirmation** workflow.
- **Mark reviewed** (`POST /api/patients/<id>/mark-reviewed/`) timestamps `Patient.last_chart_review_at` and flags items reviewed — audit trail beyond that is prototype-level.

---

## Cost vs API-only embedding/LLM

| | Local MiniLM path (current) | API-only embeddings + LLM |
|--|------------------------------|----------------------------|
| Marginal API $ / query | ~$0 | Per-token / per-call fees |
| Privacy / control | Stays on machine during encode | Data leaves perimeter unless self-hosted |
| Latency | Cold start + CPU encode; afterward moderate | Network RTT + provider queues |
| Reproducibility | Pin package + model name | Depends on vendor versioning |
| Quality ceiling | General-domain semantics | Stronger frontier models — at cost |

---

## Failure cases

1. **Semantic false positives** — paraphrases match without clinical utility; users must read snippet + source trail.
2. **Parser misses** — unusual lab layout, shorthand, pasted noise → empty or incomplete extraction.
3. **Stale embeddings** — new reports not reindexed/embeded → semantic gap until `rebuild_embeddings`.
4. **Cold start / download** — first `SentenceTransformer` load can take noticeable time and needs disk for cache.

---

## Commands (reference)

```bash
cd backend
python manage.py seed_demo_data
python manage.py rebuild_embeddings --reindex-first
python manage.py rebuild_embeddings --patient-id 1   # optional single patient
```

---

## Evaluation quick checks (demo)

- **Sarah Johnson** (MRN `1058846`): CA 19--9 trajectory, pancreatic ADC profile, imaging language.
- **Michael Chen** (MRN `1042201`): Chromogranin A, NET vocabulary, MRI/lesion wording.
- **Semantic query examples:** see root `README.md` example list.

Automated Django tests (`python manage.py test`) cover parsers, rule flags, hybrid search hooks, workspace payloads, chart-review API behavior, etc.
