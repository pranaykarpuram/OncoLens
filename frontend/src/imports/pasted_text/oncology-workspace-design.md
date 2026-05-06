Revise the current OncoLens design. The current version looks too much like a generic AI-generated healthcare dashboard. Shift the product from a normal patient dashboard into an oncology chart-review workspace.

The app should feel like an evidence-first clinical tool for doctors who need to quickly find and verify information across reports, labs, notes, and timelines. It should not look like a consumer wellness app or generic SaaS dashboard.

New product positioning:
OncoLens is an evidence-first chart review accelerator for oncology.
It helps oncologists answer questions like:
- What changed since the last visit?
- Where is the evidence for progression concern?
- Which reports mention KRAS?
- What data is missing before tumor board?
- Which patients need chart review today?

Important design direction:
- Remove the large generic blue gradient hero card from the dashboard.
- Remove any circular “risk score” or “priority score” visual. It feels medically unsafe and too generic.
- Make the UI calmer, sharper, and more document-focused.
- Use less bright blue. Use a mostly white / very light slate interface with navy text, subtle blue accents, and carefully used amber/red flags.
- Make it feel like a premium clinical workspace, not an AI template.
- Use personality through thoughtful layout, clean typography, small icons, and evidence cards.
- Prioritize fast reading, source verification, and low cognitive load.

Revise navigation:
Sidebar items should be:
1. Review Queue
2. Patients
3. Evidence Search
4. Report Intake
5. Tumor Board
6. Analytics
7. Team
8. Settings

Main landing page should become “Review Queue,” not generic Dashboard.

SCREEN 1: Review Queue

Purpose:
A doctor starts here to see what needs chart review today.

Top:
Title: “Review Queue”
Subtitle: “Patients with new reports, changed trends, or missing follow-up data.”

Top action/search bar:
Large command-style search input:
“Ask across your panel: rising CA 19-9, missing labs, KRAS mutation…”

Main layout:
Left column, 70% width:
A list of patient review cards.

Each review card should include:
- patient name
- diagnosis and stage
- current treatment
- why this patient is in the queue
- newest source document
- key changed data
- button: “Open Review Workspace”

Example card:
Sarah Johnson
Pancreatic adenocarcinoma · Stage III · FOLFIRINOX
Why review:
- CA 19-9 increased across 3 measurements
- Latest note mentions fatigue and weight loss
- CT report uploaded yesterday
Newest evidence:
- CT Abdomen/Pelvis · Apr 22, 2026
CTA: Open Review Workspace

Right column:
“Today’s Intake”
- 6 new reports parsed
- 3 need confirmation
- 4 patients with new evidence
- 2 missing recent labs

Below:
Small “Safety model” card:
“OncoLens surfaces source-backed observations. It does not diagnose, prescribe, or replace clinician judgment.”

SCREEN 2: Patient Review Workspace

This is the core screen.

Top compact patient header:
Sarah Johnson
MRN 1058846 · 62F · Pancreatic adenocarcinoma · Stage III
Current treatment: FOLFIRINOX
Buttons: Upload Report, Add Note, Export Brief

Directly under header:
Large chart question bar:
“Ask this chart…”

Placeholder examples:
- What changed since the last visit?
- Show evidence related to progression
- Find all KRAS mentions
- Summarize latest imaging and labs
- What data is missing?

Use chips below:
What changed? · Progression evidence · Lab trends · Imaging mentions · Missing data

Main workspace should be 3-column:

LEFT COLUMN: Timeline
Title: “Timeline”
Vertical timeline with filters:
All · Labs · Imaging · Notes · Treatment · Pathology

Timeline events:
Apr 27 — Oncology note — Fatigue and weight loss mentioned
Apr 22 — CT report — New imaging report uploaded
Mar 29 — Lab — CA 19-9 780 U/mL
Mar 01 — Lab — CA 19-9 310 U/mL
Feb 02 — Treatment — FOLFIRINOX started

CENTER COLUMN: Evidence Board
Title: “Evidence Board”
Subtitle: “Source-backed observations from this chart”

This column should show evidence cards, not generic AI cards.

Evidence card format:
- observation title
- source-backed explanation
- data points
- source chips
- confidence / extraction status
- button: View Source

Example evidence cards:

Card 1:
Title: “CA 19-9 increased across consecutive labs”
Data:
120 → 310 → 780 → 910 U/mL
Sources:
Lab Report Feb 02, Mar 01, Mar 29, Apr 22
Footer:
Rule: same marker increased across 3+ consecutive observations
Button: View source trail

Card 2:
Title: “Latest note contains symptom worsening language”
Evidence:
“fatigue” and “weight loss” detected in Apr 27 oncology note
Button: Open note snippet

Card 3:
Title: “Imaging report includes progression-related language”
Evidence:
Snippet from CT report mentioning lesion size change
Button: Open imaging report

Card 4:
Title: “Missing follow-up lab”
Evidence:
No bilirubin value found after Apr 02
Button: Review missing data

RIGHT COLUMN: Source Viewer
Title: “Source Viewer”
Default state:
“Select evidence to view the exact report snippet.”

When evidence selected:
Show source document title:
CT Abdomen/Pelvis · Apr 22, 2026
Show highlighted text snippet.
Show extracted fields from that source.
Buttons:
Open full report · Mark reviewed

This right panel is extremely important because it makes the AI explainable.

SCREEN 3: Evidence Search

Purpose:
Search across all patients and documents.

Search-first design.
Large search bar:
“Search evidence across reports, notes, labs, and biomarkers…”

Suggested searches:
Rising CA 19-9 · KRAS mutation · possible progression · fatigue · missing labs · FOLFIRINOX

Results should be evidence cards, not generic result cards.
Each result:
- matched patient
- matched source
- highlighted snippet
- structured extracted value if available
- date
- button: Open in Review Workspace

Add left filters:
Patient status
Source type
Date range
Biomarker
Treatment
Reviewed / unreviewed

SCREEN 4: Report Intake

Purpose:
This is not just “Upload Report.” It is an intake workflow.

Layout:
Left side:
Upload or paste report.
Select patient.
Select report type.

Center:
Extraction progress:
1. Text detected
2. Clinical entities extracted
3. Values mapped
4. Needs clinician confirmation

Right side:
Extraction Review

Show extracted fields grouped by:
- Report metadata
- Lab values
- Biomarkers / mutations
- Symptoms
- Treatment mentions
- Imaging language
- Uncertain extractions

Each extraction row:
- field
- value
- source snippet
- confidence
- edit
- confirm checkbox

Bottom:
Confirm & Update Evidence Board

Add warning:
“Values are not added to the chart until confirmed.”

SCREEN 5: Tumor Board Brief

Purpose:
Generate a concise pre-meeting brief.

Layout:
Patient selector at top.
Brief sections:
- One-line case summary
- Current treatment course
- Key timeline events
- Evidence of change
- Missing data
- Source documents used

Each statement must have source chips.
Button:
Export Brief

This screen gives the app personality and oncology specificity.

Visual redesign requirements:
- Remove giant generic cards where possible.
- Use compact information-dense cards, but keep spacing readable.
- Use typography and structure more than color.
- Use subtle slate/blue palette:
  background #F8FAFC
  surface #FFFFFF
  border #E2E8F0
  text #0F172A
  secondary #64748B
  blue #2563EB
  cyan accent #0EA5E9
  amber #F59E0B
  red #DC2626
- Use blue for actions, amber/red only for attention.
- Cards should have 16–20px radius, not overly bubbly.
- Reduce gradient usage; use it only in logo or tiny accents.
- Avoid huge avatars and decorative icons.
- Make the interface feel like Notion + Linear + a clinical research tool.
- Keep it simple, fast, and evidence-first.

Microcopy rules:
Do not say:
- AI diagnosis
- predicted progression
- recommended treatment
- risk score

Say:
- source-backed observation
- evidence found
- may warrant clinician review
- extracted from uploaded report
- clinician confirmation required

The final design should make the difference clear:
Epic/Cerner store the chart.
OncoLens helps doctors find and verify the evidence inside the chart faster.