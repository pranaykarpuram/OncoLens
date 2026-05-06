Final refinement pass for OncoLens. Do not redesign from scratch. Keep the current structure, but polish the product until it feels like a premium, focused, evidence-first oncology chart review tool.

The current direction is correct:
OncoLens is NOT a patient dashboard.
OncoLens is NOT an EHR replacement.
OncoLens is an evidence-first oncology chart review layer.

Epic/Cerner store the chart.
OncoLens helps doctors find, organize, compress, and verify the evidence inside the chart faster.

Make the final design clearly communicate these 5 core values:
1. Evidence retrieval — find exact relevant chart evidence faster.
2. Evidence organization — bring labs, notes, imaging, pathology, extracted values, and missing data into one review flow.
3. Evidence compression — show what changed without forcing the doctor to manually reconstruct the chart.
4. Workflow-specific outputs — Review Queue, Evidence Search, Report Intake, Tumor Board Brief.
5. Explainability — every generated observation is source-backed, clickable, and reviewable.

GLOBAL UI POLISH

Make the interface feel:
- sharper
- tighter
- calmer
- more intentional
- more premium
- less generic SaaS
- less “AI generated”
- more like Linear + Notion + a clinical research workspace

Do not add more decoration. Add polish through spacing, typography, hierarchy, alignment, and microcopy.

Visual refinements:
- Reduce excess whitespace slightly across cards.
- Tighten vertical rhythm.
- Make card heights more purposeful.
- Use fewer oversized icons.
- Keep border radius mature: cards 14–16px, buttons/inputs 12–14px.
- Use subtle dividers instead of too many nested cards.
- Keep blue only for primary actions and active states.
- Use amber for review-needed observations.
- Use red only sparingly for urgent or unresolved confirmation issues.
- Keep backgrounds light: #F8FAFC / #FFFFFF.
- Keep text high contrast: #0F172A.
- Keep secondary text: #64748B.
- Keep borders: #E2E8F0.

GLOBAL LANGUAGE CLEANUP

Replace all generic dashboard/profile language with evidence-first language.

Rename:
- “Open Profile” → “Open Workspace”
- “View source” → “View Source Trail”
- “Insight flags” → “Source-backed Observations”
- “Risk” or “Priority” → “Review Status”
- “AI Summary” → “Evidence Summary”
- “Dashboard” → do not use dashboard language
- “Patient Profile” → “Review Workspace”

Avoid:
- AI prediction
- risk score
- diagnosis generated
- treatment recommendation
- smart diagnosis
- patient risk
- recommended therapy

Use:
- source-backed observation
- evidence found
- source trail
- extracted value
- needs confirmation
- clinician review required
- review workspace
- what changed
- missing data
- confirmed source
- unconfirmed extraction

SIDEBAR

Keep sidebar minimal and final:

Primary:
1. Review Queue
2. Evidence Search
3. Report Intake
4. Tumor Board

Secondary:
5. Patients
6. Admin

Do not include Review Workspace as a sidebar item. It is contextual and opened from queue/search/patient rows.

Tighten sidebar:
- narrower if possible
- slightly smaller logo block
- compact nav spacing
- subtle active state
- simple line icons
- no bulky pills
- bottom user card compact

REVIEW QUEUE PAGE

This page is the home screen and should feel like a prioritized chart-review worklist.

Title:
“Review Queue”

Subtitle:
“Charts with new reports, changed trends, missing data, or unreviewed evidence.”

Top command bar:
“Ask across your panel: rising CA 19-9, missing labs, KRAS mutation…”

Filter pills:
- New Evidence
- Missing Data
- Needs Confirmation
- Unreviewed Sources

Refine queue cards:
Each card should feel like a task the doctor can complete, not a patient profile.

Card hierarchy:
1. Patient name + MRN
2. diagnosis · stage · treatment
3. Review status badge
4. “Why this chart is in queue”
5. evidence bullets
6. newest evidence block
7. CTA: “Open Workspace”

Make “Why this chart is in queue” the visual focus.

Example card copy:
Sarah Johnson
MRN 1058846
Pancreatic adenocarcinoma · Stage III · FOLFIRINOX
Review Status: Needs Review

Why this chart is in queue:
- Consecutive CA 19-9 increase found
- Latest note mentions fatigue and weight loss
- CT report uploaded yesterday

Newest evidence:
CT Abdomen/Pelvis · Apr 22, 2026

Button:
Open Workspace

Right rail:
Keep compact.
Cards:
1. Today’s Evidence Intake
2. Review Philosophy
3. Quick Actions

Today’s Evidence Intake:
- New reports parsed: 6
- Need confirmation: 3
- Patients with new evidence: 4
- Missing recent labs: 2

Review Philosophy:
“OncoLens surfaces source-backed observations. It does not diagnose, prescribe, or replace clinician judgment.”

Quick Actions:
- Upload report
- Search evidence
- Generate tumor board brief

PATIENT REVIEW WORKSPACE

This is the most important screen. Make it feel like the heart of the product.

Title:
“Patient Review Workspace”

Subtitle:
“Evidence-first chart review”

Top context card:
Make compact and sticky-feeling.

Include:
Sarah Johnson
MRN 1058846 · 62F · Pancreatic adenocarcinoma · Stage III
Current treatment: FOLFIRINOX
Last updated: Apr 27, 2026

Buttons:
- Upload Report
- Add Note
- Export Brief

Main command bar:
“Ask this chart: What changed since last visit?”

Question chips:
- What changed?
- Show progression evidence
- Find KRAS mentions
- Summarize latest imaging
- Missing data
- Lab trends
- Prepare tumor board brief

Main layout:
3 columns:
Left: Timeline
Center: Evidence Board
Right: Source Viewer

LEFT: Timeline
Make compact and scannable.
Use small source-type icons:
- Lab
- Imaging
- Note
- Treatment
- Pathology

Filters:
All · Labs · Imaging · Notes · Treatment · Pathology

Timeline entries:
Apr 27 — Oncology note — fatigue and weight loss mentioned
Apr 22 — CT report — imaging report uploaded
Mar 29 — Lab — CA 19-9: 780 U/mL
Mar 01 — Lab — CA 19-9: 310 U/mL
Feb 02 — Treatment — FOLFIRINOX started

CENTER: Evidence Board
Rename heading to:
“Evidence Board”

Subtitle:
“Source-backed observations from this chart.”

Cards should be called source-backed observation cards.

Evidence Card design:
- Use amber left border for review-needed observation
- Avoid aggressive red unless unresolved/urgent
- Show title, data, source chips, reason line, action
- Make source chips visually clean and clickable
- Button should say “View Source Trail”

Example card 1:
Title:
“Consecutive CA 19-9 increase found”

Data:
120 → 310 → 780 → 910 U/mL

Explanation:
“Extracted lab observations show a consecutive increase across four measurements.”

Source chips:
Lab Report · Feb 02
Lab Report · Mar 01
Lab Report · Mar 29
Lab Report · Apr 22

Reason line:
“Flagged because the same marker increased across 3+ consecutive observations.”

Button:
View Source Trail

Example card 2:
Title:
“Symptom worsening language found”

Explanation:
“Apr 27 oncology note includes mentions of fatigue and weight loss.”

Source chip:
Oncology Note · Apr 27

Button:
View Source Trail

Example card 3:
Title:
“Progression-related imaging language found”

Explanation:
“CT report includes language related to lesion size change.”

Source chip:
CT Abdomen/Pelvis · Apr 22

Button:
View Source Trail

Example card 4:
Title:
“Recent bilirubin value missing”

Explanation:
“No bilirubin observation found after Apr 02.”

Source chip:
Lab history

Button:
Review missing data

RIGHT: Source Viewer
This panel must communicate trust and explainability.

Default empty state:
“Select an evidence card or timeline event to view the exact source sentence, extracted values, and report metadata.”

When selected, show a filled state:
Document:
CT Abdomen/Pelvis
Date:
Apr 22, 2026
Type:
Imaging report
Status:
Needs confirmation

Highlighted Source Snippet:
“Interval increase in size of pancreatic head lesion compared with prior study…”

Extracted fields:
- Key language: lesion size increase
- Source type: Imaging
- Extraction confidence: 91%
- Confirmation status: Unconfirmed

Buttons:
- Open Full Report
- Mark Reviewed

Footer:
“Source-backed observation. Clinician review required.”

EVIDENCE SEARCH PAGE

This screen should feel like the app’s superpower.

Title:
“Evidence Search”

Subtitle:
“Search across reports, notes, labs, biomarkers, timelines, and extracted values.”

Search bar:
“Search evidence: rising CA 19-9, KRAS mutation, fatigue, missing labs…”

Suggested chips:
- Rising CA 19-9
- KRAS mutation
- Possible progression
- Missing bilirubin
- FOLFIRINOX
- Fatigue
- Weight loss
- CT lesion size

Refine results:
Each result should be evidence-first, not patient-first.

Result card hierarchy:
1. matched evidence / snippet
2. patient + MRN
3. source type + date
4. extracted value
5. why this matched
6. confidence / status
7. actions

Example:
Matched snippet:
“CA 19-9 increased from 310 to 780 U/mL, elevated from prior measurement…”

Patient:
Sarah Johnson · MRN 1058846

Source:
Lab Report · Mar 29, 2026

Extracted Value:
CA 19-9: 780 U/mL

Why this matched:
Matched tumor marker trend query

Confidence:
96%

Buttons:
Open Workspace
View Source Trail

Use subtle highlighted text for matched terms.
Make “Extracted Value” and “Why This Matched” compact, not huge boxes.
Add “Source Trail” link consistently.

REPORT INTAKE PAGE

This page should show the AI/data workflow clearly.

Title:
“Report Intake”

Subtitle:
“Turn uploaded reports into structured, reviewable chart evidence.”

Use a 3-step process:
1. Upload
2. Extract
3. Confirm

Show two states if possible:
- Upload empty state
- Extraction review state

Upload area:
- Drag and drop report
- Paste report text
- Select patient
- Select report type
- Start extraction button

Extraction Review state:
Grouped sections:
- Metadata
- Lab values
- Biomarkers
- Symptoms
- Treatment mentions
- Imaging language
- Uncertain fields

Each extracted row:
- field name
- extracted value
- source snippet
- confidence
- edit button
- confirm checkbox

Add confirmation queue:
“3 extracted values need clinician confirmation.”

Important copy:
“Extracted values are not added to the Evidence Board until confirmed.”

Success state:
“Evidence added to Sarah Johnson’s Review Workspace.”

TUMOR BOARD PAGE

Rename page:
“Tumor Board Brief”

Purpose:
Generate an exportable, source-backed case brief.

Top:
Patient selector
Generate Brief button
Export Brief button

Brief should look like a clean document, not a dashboard card.

Sections:
1. Case Summary
2. Current Treatment Course
3. Key Timeline Events
4. Evidence of Change
5. Missing or Unconfirmed Data
6. Source Documents Used

Every important statement should include small source chips.

Example:
“FOLFIRINOX initiated Feb 02, 2026.”
Source chip:
Treatment Note · Feb 02

Make the brief compact, readable, and export-ready.

PATIENTS PAGE

This is secondary, not the product centerpiece.

Use concise patient rows.

Columns:
- Patient
- Diagnosis
- Treatment
- Latest evidence
- Review status
- Last updated
- Action

Action button:
“Open Workspace”

Do not use “Open Profile.”

ADMIN PAGE

Admin should include:
- team management
- access levels
- compact analytics/reporting
- export data

Keep admin secondary and simple.

COMPONENT CONSISTENCY

Create and reuse these components consistently:

1. ReviewQueueCard
2. EvidenceCard
3. SourceChip
4. SourceViewerPanel
5. ChartQuestionBar
6. TimelineEvent
7. ExtractionRow
8. ConfirmationBadge
9. MissingDataCard
10. TumorBoardBriefSection
11. SafetyNote
12. ReviewStatusBadge

Make all components feel part of one design system.

FINAL DESIGN CHECKLIST

The final design should clearly communicate:

- This is not an EHR replacement.
- This is not a generic patient dashboard.
- This is not an AI doctor.
- This is a source-backed oncology chart review workspace.

The final UI should make it obvious that OncoLens helps doctors:
1. Find evidence faster.
2. Organize scattered chart data.
3. Compress what changed.
4. Produce workflow-specific outputs.
5. Verify every observation through source trails.

When done, the interface should feel ready to implement as a polished class prototype and believable as the first version of a serious healthcare product.