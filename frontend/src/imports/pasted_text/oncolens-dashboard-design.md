Create a polished, production-quality healthcare web application frontend called “OncoLens” — a Smart Oncology Profile System for oncologists reviewing complex pancreatic cancer patients.

The product is NOT a full hospital EHR. It is an intelligent clinical profile layer that organizes fragmented oncology data into a fast, clear, visually intuitive interface. The interface should feel modern, calm, clinical, premium, and extremely easy to understand at first glance.

Use the attached inspiration image as the visual direction:
- soft medical blue gradient backgrounds
- rounded cards
- clean glassmorphism / frosted panels
- subtle depth and shadows
- blue-white healthcare palette
- spacious layout
- friendly but professional design
- modern mobile-health visual language, but build this as a desktop web app
- use glowing blue accents sparingly
- use soft anatomical / oncology-themed abstract background visuals, not distracting

The app should be designed for doctors, not patients. The doctor should be able to open the app and understand patient status in seconds.

Overall design goals:
1. Minimal cognitive load
2. Fast patient review
3. Clear information hierarchy
4. No clutter
5. No scary “AI doctor” tone
6. Explainable insights with source evidence
7. No direct treatment recommendations
8. Everything should feel clinically safe and trustworthy
9. Important information should be visible immediately
10. The interface should be self-explanatory

Use a desktop layout size of 1440px wide. Make all pages responsive-friendly, but prioritize desktop.

Brand:
App name: OncoLens
Tagline: “Clearer oncology profiles. Faster clinical review.”
Logo idea: simple lens / circular scan icon combined with a subtle cell or oncology dot pattern.

Color palette:
- Primary background: #F6FAFF
- Deep navy text: #0F172A
- Secondary text: #64748B
- Muted text: #94A3B8
- Primary blue: #2563EB
- Bright clinical blue: #38BDF8
- Soft blue surface: #EAF4FF
- Card white: #FFFFFF
- Border: #E2E8F0
- Success green: #16A34A
- Watch amber: #F59E0B
- Needs review red: #DC2626
- Purple accent for AI: #7C3AED
Use gradients like #2563EB to #38BDF8 for selected states and hero elements.

Typography:
Use a clean modern sans-serif font similar to Inter or SF Pro.
Headings should be bold but not heavy.
Use strong visual hierarchy:
- Page title: 28–32px
- Section headings: 18–20px
- Card labels: 12–13px uppercase or muted
- Body text: 14–16px
- Important clinical values: 22–28px

Core layout:
Create a dashboard web app with:
- left vertical sidebar
- top header bar
- main content area
- rounded cards
- consistent spacing
- reusable components

Sidebar:
Width around 84px collapsed icon sidebar or 240px expanded sidebar. Prefer expanded sidebar for clarity.
Sidebar background: white with slight border.
Top of sidebar: OncoLens logo.
Navigation items:
1. Dashboard
2. Patients
3. Reports
4. Search
5. Analytics
6. Team
7. Settings
Bottom sidebar:
- logged-in user mini profile
- role badge: Doctor
Use icons for each nav item.
Selected nav item should have soft blue pill background and blue icon.

Top header:
Height 72px.
Left side:
- current page title
- short subtitle
Right side:
- global search input: “Search patients, reports, biomarkers…”
- notification bell
- user avatar
- role pill: “Oncologist”
Header should feel clean, not crowded.

Create the following screens/components in the design:

SCREEN 1: Login Page

Goal:
Professional medical login screen.

Layout:
Split screen.
Left side:
- soft blue gradient medical illustration area
- abstract 3D cell / pancreas / lens visual
- headline: “Clinical clarity for complex oncology cases.”
- subtext: “Organize reports, labs, timelines, and insight flags into one patient profile.”

Right side:
- login card
- OncoLens logo
- title: “Welcome back”
- email input
- password input
- role selector dropdown with Doctor, Nurse, Admin
- primary button: “Sign in”
- small text: “Prototype clinical decision support interface”
- footer disclaimer: “For demonstration only. Not for diagnosis or treatment decisions.”

Use rounded 24px login card, soft shadow, lots of white space.

SCREEN 2: Main Dashboard

Goal:
Doctor sees high-level overview of patient panel.

Main content:
Top greeting card:
- “Good morning, Dr. Morgan”
- “12 patients updated this week. 4 require review.”
- small abstract oncology visual on right
- primary CTA button: “Review flagged patients”

Metric cards row:
1. Total Patients: 28
2. Needs Review: 4
3. Reports Parsed: 126
4. Missing Recent Labs: 3

Each metric card:
- icon
- label
- number
- small trend note

Below:
Two-column layout.

Left large card: “Priority Patients”
Table/card list with 5 patients.
Columns:
- Patient
- Diagnosis
- Current Treatment
- Latest Signal
- Status
- Last Updated
Use status badges:
- Stable: green
- Watch: amber
- Needs Review: red
Each row should have a “Open profile” button/icon.

Right card: “Recent Report Activity”
List uploaded reports:
- Pathology Report parsed
- Imaging Report needs review
- Lab Panel extracted
Each item shows time, patient name, report type, parsing status.

Bottom card: “System Notes”
Show safe language:
- “Insight flags are observation-based and require clinician review.”
- “No treatment recommendations are generated.”

SCREEN 3: Patient Directory

Goal:
Doctor can quickly find the right patient.

Top:
Page title: “Patients”
Subtitle: “Search and review oncology profiles.”

Controls:
- Search bar: “Search by name, MRN, mutation, treatment…”
- Filter chips: All, Stable, Watch, Needs Review, Missing Labs
- Sort dropdown: Last updated, Risk status, Name

Patient list:
Use premium rounded cards or a clean table. Prefer hybrid card-table.

Each patient row/card includes:
- patient avatar/initials
- name: Sarah Johnson
- MRN
- age/sex
- diagnosis: Pancreatic adenocarcinoma
- stage: Stage III
- current treatment: FOLFIRINOX
- key biomarkers: KRAS+, TP53+
- latest CA 19-9 value with mini trend arrow
- status badge
- last updated
- button: “Open Profile”

Include 8 sample patients with varied statuses.

SCREEN 4: Smart Patient Profile Dashboard

This is the most important screen. Make it extremely polished and visually clear.

Page header:
Left:
- Back to Patients
- Patient name: Sarah Johnson
- MRN: 1058846
- 62F
- Diagnosis: Pancreatic adenocarcinoma
- Stage III
- Current Treatment: FOLFIRINOX
Right:
- status badge: Needs Review
- buttons: Upload Report, Add Note, Export Summary

Layout:
Use 12-column grid.

Top row:
1. Large Clinical Snapshot card, left 8 columns
2. Patient Status card, right 4 columns

Clinical Snapshot card:
Title: “Clinical Snapshot”
Subtext: “Updated from latest reports and notes”
Inside use clean summary chips:
- Diagnosis: Pancreatic adenocarcinoma
- Stage: III
- Current Therapy: FOLFIRINOX
- Biomarkers: KRAS G12D, TP53
- Latest CA 19-9: 780 U/mL
- Last Imaging: 04/20/2026
- Last Visit: 04/27/2026

Add AI summary box inside the card:
Header: “Generated Clinical Summary”
Use purple/blue AI icon.
Text:
“Source documents show the patient is undergoing FOLFIRINOX treatment. CA 19-9 has increased across the last three recorded measurements, and the latest note mentions fatigue and weight loss. This summary is observation-based and requires clinician review.”

Add small disclaimer:
“Not a diagnosis or treatment recommendation.”

Patient Status card:
Display circular status visualization or score-like ring, but do NOT call it risk score if unsafe. Call it “Review Priority.”
- Review Priority: High
- 3 active insight flags
- 2 reports added this month
- 1 missing follow-up item
Use red/amber/green status chips.

Second row:
Left 7 columns: Trend Dashboard
Right 5 columns: Insight Flags

Trend Dashboard card:
Title: “Longitudinal Trends”
Tabs: Tumor Markers, Vitals, Labs
Show line chart for CA 19-9:
- Feb 02: 120
- Mar 01: 310
- Mar 29: 780
- Apr 22: 910
Y-axis label: CA 19-9 (U/mL)
Under chart, show mini stat cards:
- Latest: 910 U/mL
- Change: +192% over 8 weeks
- Pattern: Consecutive increase
Add note:
“Trend flag generated from structured lab observations.”

Also include secondary mini trend for Weight:
- 70kg → 66kg
Show small downward sparkline.

Insight Flags card:
Title: “Insight Flags”
Subtitle: “Observation-based signals”
List 4 flags:
1. Needs Review — “CA 19-9 increased across last 3 measurements”
2. Watch — “Weight decreased over last 2 visits”
3. Watch — “Latest note mentions fatigue”
4. Info — “No treatment recommendation generated”
Each flag:
- severity icon
- title
- one-line explanation
- “View evidence” link/button
Use safe wording only.

Third row:
Left 8 columns: Clinical Timeline
Right 4 columns: Source Documents

Clinical Timeline card:
Title: “Clinical Timeline”
Vertical timeline with dated events:
- Jan 12: Diagnosis recorded
- Jan 20: Pathology report uploaded
- Feb 02: FOLFIRINOX started
- Mar 01: Lab report parsed
- Mar 29: CA 19-9 increased
- Apr 20: Imaging report uploaded
- Apr 27: Clinical note added
Each event has icon and short description.
Use color-coded dots by event type.

Source Documents card:
Title: “Source Documents”
List documents:
- Pathology Report — Parsed
- Lab Panel — Parsed
- CT Imaging Impression — Needs Review
- Oncology Visit Note — Parsed
Each document has:
- type icon
- date
- status pill
- button: View
At bottom: Upload Report button.

Fourth row:
Full width: Extracted Structured Data table
Columns:
- Date
- Source
- Data Type
- Name
- Value
- Unit
- Confidence
- Verified
Rows:
- CA 19-9, 120, U/mL, 94%, Verified
- CA 19-9, 310, U/mL, 96%, Verified
- Weight, 66, kg, 91%, Pending
- KRAS G12D, mutation, 88%, Verified
Use confidence pills and verified checkmarks.

SCREEN 5: Report Upload + Extraction Review

Goal:
Doctor/nurse uploads a report, system extracts fields, user confirms before saving.

Layout:
Page title: “Upload Report”
Subtitle: “Extract structured oncology data from clinical reports.”

Two-column layout:
Left card: Upload Panel
- drag-and-drop upload area
- accepts PDF, TXT, DOCX for prototype
- button: “Upload report”
- optional text area: “Paste report text”
- dropdown: Report type: Auto-detect, Lab, Pathology, Imaging, Oncology Note
- patient selector dropdown

Right card: Extraction Preview
Before upload:
- empty state illustration
- text: “Extracted fields will appear here.”

After upload state:
Show progress steps:
1. File uploaded
2. Text extracted
3. Entities identified
4. Ready for review
Use status visibility.

Extraction result sections:
- Report Metadata
  - Report date
  - Report type
  - Patient match
- Extracted Labs
  - CA 19-9: 780 U/mL
  - Bilirubin: 1.4 mg/dL
- Extracted Biomarkers
  - KRAS G12D
  - TP53
- Extracted Symptoms
  - fatigue
  - weight loss
- Extracted Clinical Language
  - “possible progression” phrase detected

Each extracted item has:
- confidence %
- source snippet button
- edit icon
- checkbox to confirm

Bottom buttons:
- Cancel
- Save as Draft
- Confirm & Update Profile

Add safety copy:
“Clinician confirmation required before extracted values update the patient profile.”

SCREEN 6: Insight Evidence Drawer / Modal

Goal:
When doctor clicks “View evidence,” show exactly why a flag exists.

Design:
Slide-over drawer from right side, width 480px, rounded left corners.

Header:
- Insight title: “CA 19-9 increased across last 3 measurements”
- severity badge: Needs Review
- close icon

Body:
Section 1: Why this was flagged
Text:
“This flag was generated because CA 19-9 increased on three consecutive recorded observations.”

Section 2: Evidence used
Small table:
- 02/02/2026 — 120 U/mL — Lab Report
- 03/01/2026 — 310 U/mL — Lab Report
- 03/29/2026 — 780 U/mL — Lab Report
- 04/22/2026 — 910 U/mL — Lab Report

Section 3: Source snippets
Cards with report snippets:
“CA 19-9 measured at 780 U/mL…”
“CA 19-9 measured at 910 U/mL…”

Section 4: Rule logic
Show simple transparent rule:
“Flag if same marker increases across 3 consecutive measurements.”

Footer:
Buttons:
- Mark reviewed
- Open source report

Safety note:
“This insight is informational and does not determine diagnosis or treatment.”

SCREEN 7: Semantic Search Page

Goal:
Doctor can search across patients, reports, notes, and extracted fields.

Page title: “Clinical Search”
Subtitle: “Search across reports, notes, biomarkers, and timelines.”

Top:
Large search input:
Placeholder: “Try ‘rising CA 19-9’, ‘KRAS mutation’, ‘fatigue after chemotherapy’…”

Suggested chips:
- Rising CA 19-9
- KRAS mutation
- Possible progression
- Missing labs
- FOLFIRINOX

Results layout:
Left filters:
- Patients
- Reports
- Notes
- Biomarkers
- Date range
- Status

Main results:
Each result card:
- patient name
- source type
- matched snippet
- relevance score
- date
- button: Open patient
- button: View source

Example result:
Sarah Johnson — Lab Report — “CA 19-9 increased from 310 to 780 U/mL…” — 94% match.

Add explanation:
“Search uses semantic matching across indexed clinical text and extracted structured data.”

SCREEN 8: Analytics / Overview Page

Goal:
Show data feature and system-level monitoring.

Page title: “Analytics”
Subtitle: “Panel-level view of extracted oncology data.”

Top metric cards:
- Total Patients: 28
- Active Insight Flags: 14
- Needs Review: 4
- Reports Parsed: 126
- Missing Recent Labs: 3

Charts/cards:
1. Patient Status Distribution
- Stable, Watch, Needs Review

2. Reports by Type
- Lab, Pathology, Imaging, Notes

3. Most Common Biomarkers
- KRAS, TP53, SMAD4, CDKN2A

4. Missing Data Worklist
Table:
- Patient
- Missing item
- Last available
- Action

Export button:
- Export CSV
- Export JSON

SCREEN 9: Admin / Team Page

Goal:
Light role management screen.

Show:
- team members
- role
- department
- access level
- last active

Rows:
- Dr. Alex Morgan — Doctor — Oncology — Full clinical access
- Jamie Lee — Nurse — Oncology — Upload + notes
- Priya Shah — Admin — Operations — Patient management

Do not overbuild this screen.

Reusable Components to Design:

1. StatusBadge
States:
- Stable: green
- Watch: amber
- Needs Review: red
- Parsed: blue
- Pending Review: purple
- Verified: green
- Draft: gray

2. PatientCard
Includes patient identity, diagnosis, treatment, latest signal, status, CTA.

3. MetricCard
Icon + label + number + trend note.

4. InsightFlagCard
Severity icon + title + explanation + evidence button.

5. SourceDocumentCard
Report type + date + parsed status + action buttons.

6. TimelineEvent
Date + icon + title + description + event type color.

7. ExtractionFieldRow
Field name + value + unit + confidence + verified checkbox + source snippet link.

8. SearchResultCard
Patient + source + matched snippet + relevance + actions.

9. EmptyState
Soft illustration + short message + CTA.

10. SafetyDisclaimer
Small gray/blue info box used wherever AI-generated outputs appear.

Interaction details:
- Hover states on cards
- Active nav states
- Buttons should have clear primary/secondary hierarchy
- Insight cards should expand or open drawer
- Upload should show progress states
- Extracted fields should be editable before confirmation
- Search results should feel instant and organized
- Tables should be clean, not dense

Visual style details:
- Cards: 20–28px border radius
- Buttons: pill or rounded 14px
- Shadows: soft, subtle, never harsh
- Background: very light blue gradient or #F6FAFF
- Use faint grid/cell/hexagon medical patterns in hero areas only
- Avoid red except true “Needs Review”
- Use blue as the main action color
- Purple only for AI-generated summary/semantic features
- Use plenty of whitespace
- Keep clinical data readable and high contrast

Important product safety language:
Every AI-generated or insight area should include one of these:
- “Observation-based. Clinician review required.”
- “Generated from source documents. Not a treatment recommendation.”
- “This system supports review; it does not diagnose or prescribe.”

Tone:
The interface should feel calm, trustworthy, and precise. Do not make it look like a consumer wellness app. It should feel like a premium clinical tool with modern startup-quality UI.

Do not create random pages outside this scope. Focus on making these screens complete, cohesive, and visually polished.