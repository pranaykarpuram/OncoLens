Refine the current OncoLens design around the true product differentiator.

The current design is heading in the right direction, but the app still needs to more strongly communicate its secret sauce:

OncoLens is not a patient dashboard.
OncoLens is not an EHR replacement.
OncoLens is an evidence-first oncology chart review layer.

Epic/Cerner store the chart.
OncoLens helps doctors rapidly find, organize, compress, and verify the evidence inside the chart.

The entire workflow and UI should be centered around these 5 core value pillars:

1. Evidence Retrieval
Find exact relevant chart evidence faster across reports, notes, labs, pathology, imaging, and treatment history.

2. Evidence Organization
Bring scattered labs, notes, imaging reports, pathology findings, extracted values, and missing data into one review flow.

3. Evidence Compression
Summarize what changed without forcing the doctor to manually reconstruct the chart.

4. Workflow-Specific Outputs
Support real oncology workflows:
- Review Queue
- Patient Review Workspace
- Report Intake
- Evidence Search
- Tumor Board Brief

5. Explainability
Every generated observation, summary, or flag must be source-backed, clickable, and reviewable.

Do not make the product look like a generic healthcare dashboard with AI insight cards.
Make it feel like a clinical evidence workspace.

GLOBAL PRODUCT LANGUAGE CHANGES

Use this language throughout the app:
- “Evidence”
- “Source-backed”
- “Review Workspace”
- “What changed?”
- “Source trail”
- “Extracted from report”
- “Clinician confirmation required”
- “Open evidence”
- “View source”
- “Generate brief”
- “Missing data”
- “Chart evidence”
- “Review-ready”

Avoid:
- “AI prediction”
- “Diagnosis”
- “Risk score”
- “Treatment recommendation”
- “Smart score”
- “Suggested therapy”
- “Patient risk”
- “AI doctor”

GLOBAL DESIGN DIRECTION

Make the UI feel like:
- Linear + Notion + a clinical research workspace
- fast, precise, source-backed, calm
- made for doctors under time pressure
- slightly denser and more purposeful than a generic SaaS dashboard
- minimalist but with strong product identity

Visual style:
- white / slate / light blue base
- navy typography
- restrained blue actions
- amber/red only when attention is needed
- compact cards
- clean source chips
- subtle dividers
- less rounded/bubbly than before
- fewer oversized icons
- no giant generic gradient hero cards
- no circular priority/risk scores
- no decorative medical illustrations unless very subtle

The interface should make the user think:
“I can understand this patient’s chart faster because the evidence is already organized for me.”

MAIN NAVIGATION

Update sidebar navigation to reflect workflow, not generic modules:

1. Review Queue
2. Review Workspace
3. Evidence Search
4. Report Intake
5. Tumor Board Briefs
6. Patients
7. Analytics
8. Team
9. Settings

The first four items should feel like the heart of the product.

SCREEN 1: REVIEW QUEUE

Purpose:
This is the doctor’s starting point. It answers:
“Which charts need review today, and why?”

This page should NOT feel like a normal dashboard.
It should feel like a prioritized work queue.

Top header:
Title: “Review Queue”
Subtitle: “Charts with new reports, changed trends, missing data, or unreviewed evidence.”

Below header:
Large command/search bar:
“Ask across your panel: rising CA 19-9, missing labs, KRAS mutation…”

Right of search bar:
Small filter button: New Evidence
Small filter button: Missing Data
Small filter button: Needs Confirmation

Main content:
Create a two-column layout.

LEFT: Review Worklist, 70% width.
RIGHT: Evidence Intake Summary, 30% width.

Review Worklist cards:
Each card should feel like a chart-review task, not a patient profile card.

Card structure:
- Top row:
  Patient name
  MRN
  diagnosis/stage/treatment metadata
  review status badge

- Middle:
  Section title: “Why this chart is in queue”
  2–4 concise evidence-based reasons

- Evidence reasons should be written like:
  “CA 19-9 increased across 3 consecutive measurements”
  “CT report uploaded yesterday contains progression-related language”
  “Latest note mentions fatigue and weight loss”
  “No bilirubin value found after Apr 02”

- Bottom:
  “Newest evidence”
  source type + date + title
  e.g. “CT Abdomen/Pelvis · Apr 22, 2026”
  CTA: “Open Review Workspace”

Make “Why this chart is in queue” the visual focus.

Right rail:
Card 1: “Today’s Evidence Intake”
- New reports parsed: 6
- Need confirmation: 3
- Patients with new evidence: 4
- Missing recent labs: 2

Card 2: “Review Philosophy”
Text:
“OncoLens surfaces source-backed observations. It does not diagnose, prescribe, or replace clinician judgment.”

Card 3: “Quick Actions”
- Upload report
- Search evidence
- Generate tumor board brief

SCREEN 2: PATIENT REVIEW WORKSPACE

This is the most important screen in the entire product.

Purpose:
This screen answers:
“What changed, where is the evidence, and what should the doctor review?”

This screen should NOT feel like a patient profile page.
It should feel like a working space for chart review.

Top patient context bar:
Compact, sticky if possible.
Include:
- Patient name: Sarah Johnson
- MRN: 1058846
- Age/Sex: 62F
- Diagnosis: Pancreatic adenocarcinoma
- Stage: III
- Current therapy: FOLFIRINOX
- Last updated: Apr 27, 2026

Buttons:
- Upload Report
- Add Note
- Export Brief

Directly below:
Large chart question bar:
Placeholder:
“Ask this chart: What changed since last visit?”

Suggested question chips:
- What changed?
- Show progression evidence
- Find KRAS mentions
- Summarize latest imaging
- Missing data
- Lab trends
- Prepare tumor board brief

Main layout:
Use a 3-panel workspace.

LEFT PANEL: Timeline
Width: 25%
Title: “Timeline”
Purpose: Organizes the patient story over time.

Timeline filter chips:
All · Labs · Imaging · Notes · Treatment · Pathology

Timeline entries:
- Apr 27 — Oncology Note — fatigue and weight loss mentioned
- Apr 22 — CT Report — new imaging uploaded
- Mar 29 — Lab — CA 19-9: 780 U/mL
- Mar 01 — Lab — CA 19-9: 310 U/mL
- Feb 02 — Treatment — FOLFIRINOX started
- Jan 12 — Pathology — diagnosis confirmed

Timeline entries should be clickable and update the Source Viewer.

CENTER PANEL: Evidence Board
Width: 45–50%
Title: “Evidence Board”
Subtitle: “Source-backed observations from this chart.”

This is the main product area.

Use evidence cards. Each evidence card must include:
- observation title
- short compressed explanation
- structured data points
- source chips
- rule/reason line
- button: “View source trail”

Example evidence card 1:
Title:
“CA 19-9 increased across consecutive labs”

Data visual:
120 → 310 → 780 → 910 U/mL

Explanation:
“Extracted lab observations show a consecutive increase across four measurements.”

Source chips:
Lab Report · Feb 02
Lab Report · Mar 01
Lab Report · Mar 29
Lab Report · Apr 22

Reason line:
“Flagged because same marker increased across 3+ consecutive observations.”

Button:
“View source trail”

Example evidence card 2:
Title:
“Latest note contains symptom worsening language”

Explanation:
“Apr 27 oncology note includes mentions of fatigue and weight loss.”

Source chips:
Oncology Note · Apr 27

Button:
“Open note snippet”

Example evidence card 3:
Title:
“Imaging report contains progression-related language”

Explanation:
“CT report includes language related to lesion size change.”

Source chips:
CT Abdomen/Pelvis · Apr 22

Button:
“View imaging source”

Example evidence card 4:
Title:
“Missing follow-up lab”

Explanation:
“No bilirubin observation found after Apr 02.”

Source chips:
Lab history

Button:
“Review missing data”

Important:
The Evidence Board should not look like generic alerts. It should look like a curated evidence trail.

RIGHT PANEL: Source Viewer
Width: 25–30%
Title: “Source Viewer”
Purpose: Builds trust by showing exact source.

Default empty state:
“Select any evidence card or timeline event to view the exact source.”

Selected source state:
Show:
- document title
- report type
- date
- parsed status
- highlighted snippet
- extracted values
- confidence
- buttons: Open full report, Mark reviewed

Example:
Document:
“CT Abdomen/Pelvis”
Date:
Apr 22, 2026

Highlighted snippet:
“Interval increase in size of pancreatic head lesion compared with prior study…”

Extracted fields:
- Report type: Imaging
- Key language: lesion size increase
- Status: Needs clinician confirmation

Footer safety text:
“Source-backed observation. Clinician review required.”

SCREEN 3: EVIDENCE SEARCH

Purpose:
Search across the entire clinical evidence layer.

This screen should communicate:
“Don’t browse the chart manually. Search the evidence.”

Top:
Title: “Evidence Search”
Subtitle: “Search across reports, notes, labs, biomarkers, timelines, and extracted values.”

Large search bar:
“Search evidence: rising CA 19-9, KRAS mutation, fatigue, missing labs…”

Suggested searches:
- Rising CA 19-9
- KRAS mutation
- Possible progression
- Missing bilirubin
- FOLFIRINOX
- Fatigue
- Weight loss
- CT lesion size

Left filters:
- Source type: Labs, Imaging, Pathology, Notes, Treatment
- Patient status: Stable, Watch, Needs Review
- Date range
- Biomarker
- Treatment
- Reviewed / Unreviewed
- Extraction confidence

Main result cards:
Each result should be evidence-focused.

Result card structure:
- Patient name + MRN
- Source type + date
- Matched snippet with highlighted terms
- Extracted value if relevant
- “Why this matched”
- Source confidence/status
- Buttons:
  Open in Review Workspace
  View Source

Example:
Patient: Sarah Johnson
Source: Lab Report · Mar 29, 2026
Matched snippet:
“CA 19-9 increased from 310 to 780 U/mL…”
Extracted value:
CA 19-9: 780 U/mL
Why this matched:
“Matched tumor marker trend query”
Buttons:
Open in Review Workspace · View source

SCREEN 4: REPORT INTAKE

Purpose:
Turn messy reports into structured, reviewable evidence.

This should feel like an operational intake workflow, not just a file upload page.

Layout:
Three-step horizontal progress indicator:
1. Upload
2. Extract
3. Confirm

Left panel:
Upload area
- Drag/drop
- Paste text
- Select patient
- Select report type
- Button: “Start extraction”

Middle panel:
Extraction Preview
Show grouped extracted entities:
- Metadata
- Lab values
- Biomarkers
- Symptoms
- Treatments
- Imaging language
- Uncertain fields

Right panel:
Confirmation Queue
Show values that require human confirmation before being added.

Each extracted row:
- field name
- extracted value
- source snippet
- confidence
- edit button
- confirm checkbox

Important copy:
“Extracted values are not added to the Evidence Board until confirmed.”

After confirmation:
Show success state:
“Evidence added to Sarah Johnson’s Review Workspace.”

SCREEN 5: TUMOR BOARD BRIEFS

Purpose:
Generate a concise, source-backed case brief for oncology meetings.

This should feel different from generic summaries.
It should look like a clean exportable clinical brief.

Top:
Patient selector
Button: Generate Brief
Button: Export PDF / Export Text

Brief layout:
Document-like centered column.

Sections:
1. Case Summary
2. Current Treatment Course
3. Key Timeline Events
4. Evidence of Change
5. Missing or Unconfirmed Data
6. Source Documents Used

Every major sentence should have source chips.

Example source chip:
“Lab Report · Mar 29”
“CT Abdomen/Pelvis · Apr 22”
“Oncology Note · Apr 27”

Add disclaimer at bottom:
“Generated from source documents for clinician review. Not a diagnosis or treatment recommendation.”

SCREEN 6: PATIENTS

Purpose:
Secondary directory view, not the main product.

Keep it simple and compact.

Patient rows should include:
- name
- MRN
- diagnosis
- stage
- treatment
- latest evidence
- review status
- open workspace button

Rename “Open Profile” to “Open Workspace” everywhere.

SCREEN 7: ANALYTICS

Purpose:
Operational overview, not generic BI dashboard.

Focus metrics:
- Reports parsed
- Reports needing confirmation
- Active source-backed observations
- Patients missing recent labs
- Evidence search volume
- Tumor board briefs generated

Charts should be simple and compact.
Avoid making this page feel like the product’s main value.

SCREEN 8: TEAM

Keep simple.
Show team access levels, but do not make this screen prominent.

COMPONENT SYSTEM

Create reusable components:

1. EvidenceCard
Fields:
- title
- explanation
- data points
- source chips
- reason line
- severity/status
- view source button

2. SourceChip
Small pill with source type + date.

3. SourceViewerPanel
Shows selected source snippet and extracted values.

4. ReviewQueueCard
Shows patient + why review + newest evidence + CTA.

5. ExtractionRow
Shows field + value + snippet + confidence + confirm checkbox.

6. ChartQuestionBar
Large search/command input for patient-specific questions.

7. TimelineEvent
Clickable event with date, type, and source.

8. SafetyNote
Small nonintrusive disclaimer for source-backed observations.

9. MissingDataCard
Shows absent or stale data.

10. TumorBoardBriefSection
Document-style section with source chips.

COPY STYLE

Use concise, clinical, plain language.

Good examples:
- “Evidence found”
- “Source trail”
- “Extracted value”
- “Needs confirmation”
- “Open workspace”
- “Clinician review required”
- “No recent value found”
- “Matched source text”

Bad examples:
- “AI predicts”
- “Patient is high risk”
- “Recommended treatment”
- “Diagnosis generated”
- “Smart diagnosis”
- “AI doctor”

FINAL CHECK

After refinement, the app should clearly answer:

What does OncoLens do that Epic/Cerner do not focus on?

Answer:
It turns scattered chart data into a source-backed evidence workspace for oncology review.

The final UI should make these 5 values obvious:
1. Find evidence faster.
2. Organize scattered chart data.
3. Compress what changed.
4. Produce workflow-specific outputs.
5. Keep everything explainable and source-backed.