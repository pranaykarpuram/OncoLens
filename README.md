# OncoLens

**Evidence-first oncology chart review** — a Django + React prototype that helps clinicians find, organize, and verify scattered chart evidence (reports, notes, labs, imaging language, biomarkers, source-backed observations). **Not** an EHR replacement. **Not** for diagnosis or treatment recommendation. Synthetic demo data only; **not for clinical use**.


## Demo

<!-- DEMO_VIDEO -->
<!-- Drop a YouTube / Loom / Drive embed or GIF below this line -->

_Demo video coming soon. Synthetic demo data only — not for clinical use._

## Tech stack

| Layer | Technology |
|-------|-------------|
| Backend | Django 4.2, SQLite (`backend/db.sqlite3`), session auth, `django-cors-headers` |
| Frontend | React 19, Vite, TypeScript (`frontend/`) |
| Semantic search | `sentence-transformers` (default `sentence-transformers/all-MiniLM-L6-v2`), NumPy, scikit-learn |
| Embeddings storage | `evidence.SearchIndexEntry.embedding` as JSON floats (SQLite prototype) |

## Repository layout

```
OncoLens/
├── backend/                 # Django project root (manage.py)
│   ├── accounts/           # UserProfile (doctor/nurse/admin)
│   ├── patients/           # Patient, Condition, Encounter, Treatment, ClinicalNote
│   ├── reports/           # DiagnosticReport, intake/extraction flows
│   ├── evidence/          # Observation, EvidenceItem, SourceBackedObservation,
│   │                      # SearchIndexEntry, parsers, search, ai_embeddings,
│   │                      # workspace_insights, cancer_profiles, management commands
│   ├── briefs/            # TumorBoardBrief + deterministic brief service
│   ├── core/              # SPA JSON APIs, review queue helpers, timeline, legacy HTML views
│   ├── config/settings.py # CORS allowlist includes http://localhost:5173
│   ├── requirements.txt
│   └── db.sqlite3          # created by migrate (not committed if gitignored locally)
├── frontend/               # Vite SPA; proxies /api → Django :8000
├── docs/                   # e.g. oncolens_technical_report.tex, product_scope.md
├── README_AI.md           # AI workflow and model notes
└── README.md               # this file
```

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py rebuild_embeddings --reindex-first
python manage.py runserver
```

- **First embedding run** downloads model weights to the Hugging Face cache (e.g. `~/.cache/huggingface`). Weights are **not** stored in the repo.
- Optional: `export ONCOLENS_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2` (this is the default when unset).

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open the app at **http://localhost:5173** (Vite). Ensure Django is on **http://127.0.0.1:8000** so `/api` proxying works.

## Demo logins (`seed_demo_data`)

| Username | Password | Role (UserProfile) |
|----------|----------|--------------------|
| `alex.morgan.demo` | `password123` | Medical Oncologist (`doctor`, staff) |
| `jamie.lee.demo` | `password123` | Nurse Navigator (`nurse`) |
| `priya.shah.demo` | `password123` | Operations Admin (`admin`, superuser) |

Patients are recreated on each seed; flagship demos include **Sarah Johnson** MRN **1058846** and **Michael Chen** MRN **1042201**.

## Using the application

1. **Login** — Session cookie auth; SPA calls `/api/auth/login/`.
2. **Review Queue** — `/queue`; prioritizes charts with unreviewed flags, unconfirmed extractions, pending parses, activity since last OncoLens review, etc.
3. **Patient workspace** — `/patient/<id>`; Evidence Board, What changed / evidence summary, timeline, chart-scoped search, Source Viewer, **Mark reviewed**.
4. **Evidence Search** — `/search`; panel-wide retrieval.
5. **Report intake** — `/intake`; paste/upload path leads to extraction + confirmation workflow.
6. **Tumor board** — `/tumor-board`; generates structured briefs from chart + rules (deterministic composer, not an LLM).
7. **Admin** — `/admin`; operations snapshot via API.

Legacy Django HTML routes (e.g. `/queue/` without SPA) remain for smoke/development; primary UI is React.

## Where the AI feature lives

- **Evidence Search** and **Patient workspace “Ask this chart”** → `POST /api/evidence/search/` → `evidence/search.py` (lexical + profile boost + **local semantic** similarity when embeddings exist).
- **Rebuild index + embeddings**: `python manage.py rebuild_embeddings` (optional `--patient-id`, `--force`, **`--reindex-first`**).

## Example queries (demo corpus)

Try on `/search` or in workspace search:

` tumor marker getting worse ` · ` neuroendocrine marker rising ` · ` possible progression ` · ` missing liver labs ` · ` fatigue after treatment ` · ` Ki-67 ` · ` MEN1 ` · ` KRAS `

## Tests and build

```bash
cd backend
python manage.py check
python manage.py test
```

```bash
cd frontend
npm run build
```

## Documentation

- **`README_AI.md`** — AI vs rules, indexing commands, guardrails, failures.
- **`docs/product_scope.md`** — concise scope, users, deprioritized items, flow.
- **`docs/oncolens_technical_report.tex`** — 4–6 page technical report (assignment). Compile with a LaTeX install, e.g.  
  `pdflatex -interaction=nonstopmode -output-directory=docs docs/oncolens_technical_report.tex`

## Notes

- **Synthetic data only** — no real PHI.
- **Not HIPAA compliant** — coursework / prototype only.
- **No LLM/API keys required** for semantic search (local model). Tumor board and workspace summaries are **rule/template-based**, not GPT outputs.
- Change `SECRET_KEY` and disable `DEBUG` before any real deployment (`config/settings.py` currently ships a development key).
