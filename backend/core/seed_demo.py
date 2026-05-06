"""Synthetic oncology corpus builders used by seed_demo_data — never PHI."""

from __future__ import annotations

from datetime import date, timedelta
from django.contrib.auth.models import User

from briefs.services import generate_tumor_board_brief
from evidence.models import EvidenceItem, Observation, SourceBackedObservation
from evidence.services import generate_source_backed_observations
from patients.models import ClinicalNote, Condition, Encounter, Patient, Treatment
from reports.models import DiagnosticReport


def seed_condition_encounter(p: Patient, alex: User):
    Condition.objects.update_or_create(
        patient=p,
        name=p.primary_diagnosis,
        defaults={"stage": p.cancer_stage, "notes": "Seeded abstraction for prototyping."},
    )
    Encounter.objects.update_or_create(
        patient=p,
        summary=f"Synthetic encounter scaffolding for chart review prototyping · {p.full_name}",
        defaults={
            "encounter_type": "clinic_visit",
            "date": date.today() - timedelta(days=14),
            "provider": alex,
        },
    )


def _mk_obs_ev(
    patient,
    report,
    obs_type,
    name,
    val_num,
    unit,
    obs_date,
    snippet,
    conf,
    confirm_user,
):
    o = Observation.objects.create(
        patient=patient,
        report=report,
        observation_type=obs_type,
        name=name,
        value_text=str(val_num) if val_num is not None else "",
        value_number=val_num,
        unit=unit or "",
        observed_at=obs_date,
        source_snippet=snippet,
        confidence=conf,
        confirmation_status="confirmed",
        confirmed_by=confirm_user,
    )
    EvidenceItem.objects.create(
        patient=patient,
        source_type="observation",
        source_id=o.pk,
        title=f"{name} · extracted row",
        snippet=snippet,
        evidence_date=obs_date,
        metadata={"observation_id": o.pk},
    )
    return o


def seed_sarah_flagship(sarah: Patient, alex: User, nurse: User):
    """Strongest pancreatic adenocarcinoma demo — preserves CA19 ladder + imaging + bilirubin gap."""
    pathology = DiagnosticReport.objects.create(
        patient=sarah,
        report_type="pathology",
        title="Final pathology synopsis",
        report_date=date(2026, 1, 12),
        uploaded_by=alex,
        raw_text=(
            "Pathology Synopsis\nKRAS codon 12 substitution consistent with activating mutation nomenclature. "
            "Tumor adequate for ancillary studies."
        ),
        summary="Synthetic pathology synopsis with KRAS nomenclature for demo.",
        parse_status="parsed",
    )

    DiagnosticReport.objects.create(
        patient=sarah,
        report_type="oncology_note",
        title="Treatment initiation note · Feb",
        report_date=date(2026, 2, 2),
        uploaded_by=alex,
        raw_text="Infusion regimen documentation references FOLFIRINOX dosing discussion.",
        parse_status="parsed",
    )

    txt_lab_mar01 = DiagnosticReport.objects.create(
        patient=sarah,
        report_type="lab",
        title="Lab · Mar intake",
        report_date=date(2026, 3, 1),
        uploaded_by=alex,
        raw_text=(
            "Laboratory Report\nPatient: Sarah Johnson\nMRN: 1058846\nDate: 2026-03-01\n"
            "CA 19-9 increased from prior measurement and is currently 310 U/mL.\nTotal bilirubin was 1.1 mg/dL.\nAlbumin 3.6 g/dL."
        ),
        parse_status="parsed",
    )

    txt_lab_mar29 = DiagnosticReport.objects.create(
        patient=sarah,
        report_type="lab",
        title="Lab · Mar escalation",
        report_date=date(2026, 3, 29),
        uploaded_by=alex,
        raw_text=(
            "Laboratory Report\nPatient: Sarah Johnson\nMRN: 1058846\nDate: 2026-03-29\n"
            "CA 19-9 increased from prior measurement and is currently 780 U/mL.\nTotal bilirubin was 1.2 mg/dL.\nAlbumin 3.4 g/dL."
        ),
        parse_status="parsed",
    )

    imaging = DiagnosticReport.objects.create(
        patient=sarah,
        report_type="imaging",
        title="CT Abdomen/Pelvis · Apr staging focus",
        report_date=date(2026, 4, 22),
        uploaded_by=alex,
        raw_text=(
            "CT Abdomen/Pelvis\nPatient: Sarah Johnson\nDate: 2026-04-22\n"
            "Impression: Interval increase in size of pancreatic head lesion compared with prior study."
        ),
        summary="Demonstration excerpt only — lesion language retrieval for clinician review.",
        parse_status="parsed",
    )

    onco_note = DiagnosticReport.objects.create(
        patient=sarah,
        report_type="oncology_note",
        title="Oncology follow-up · Apr clinics",
        report_date=date(2026, 4, 27),
        uploaded_by=nurse,
        raw_text=(
            "Oncology Follow-up Note\nPatient reports increased fatigue and unintentional weight loss over "
            "the last several weeks. Currently receiving FOLFIRINOX. Plan emphasizes continued clinician review "
            "and correlation with laboratories."
        ),
        parse_status="parsed",
    )

    Observation.objects.filter(patient=sarah).delete()
    EvidenceItem.objects.filter(patient=sarah).delete()
    SourceBackedObservation.objects.filter(patient=sarah).delete()

    ca_series_front = [
        (date(2026, 2, 2), 120),
        (date(2026, 3, 1), 310),
        (date(2026, 3, 29), 780),
    ]
    for observed_at, val in ca_series_front:
        link = txt_lab_mar01 if observed_at <= date(2026, 3, 15) else txt_lab_mar29
        _mk_obs_ev(
            sarah,
            link,
            "tumor_marker",
            "CA 19-9",
            val,
            "U/mL",
            observed_at,
            f"CA 19-9 {val} U/mL on lab narrative · synthetic chart row",
            0.95,
            alex,
        )

    _mk_obs_ev(
        sarah,
        imaging,
        "tumor_marker",
        "CA 19-9",
        910,
        "U/mL",
        date(2026, 4, 22),
        "Demonstration oncology lab tie-in anchored to staging imaging cadence narrative.",
        0.9,
        alex,
    )

    Observation.objects.create(
        patient=sarah,
        report=txt_lab_mar01,
        observation_type="vital",
        name="Weight",
        value_number=70,
        unit="kg",
        observed_at=date(2026, 2, 28),
        source_snippet="Weight 70 kg (chart abstraction)",
        confidence=0.8,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )
    Observation.objects.create(
        patient=sarah,
        report=txt_lab_mar29,
        observation_type="vital",
        name="Weight",
        value_number=66,
        unit="kg",
        observed_at=date(2026, 3, 29),
        source_snippet="Weight decreased to 66 kg synthetic documentation line",
        confidence=0.8,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Observation.objects.create(
        patient=sarah,
        report=imaging,
        observation_type="imaging_language",
        name="Imaging lesion language excerpt",
        value_text="documented lesion language surfaced for clinician review only",
        source_snippet="Interval increase wording captured from synthetic CT impression block.",
        confidence=0.9,
        observed_at=date(2026, 4, 22),
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Observation.objects.create(
        patient=sarah,
        report=onco_note,
        observation_type="symptom",
        name="Fatigue burden language",
        value_text="documented symptom language surfaced for clinician review only",
        source_snippet=(
            "Patient discusses fatigue and unintended weight-loss language in oncology follow-up excerpt."
        ),
        confidence=0.82,
        observed_at=date(2026, 4, 27),
        confirmation_status="confirmed",
        confirmed_by=nurse,
    )

    Observation.objects.filter(patient=sarah, name__icontains="bilirubin").delete()

    ClinicalNote.objects.create(
        patient=sarah,
        author=nurse,
        note_type="visit",
        text="Demonstration nursing touch-base referencing fatigue wording already captured in oncology follow-up excerpts.",
        note_date=date(2026, 4, 28),
    )

    Treatment.objects.update_or_create(
        patient=sarah,
        name="FOLFIRINOX",
        defaults={
            "treatment_type": "Chemotherapy infusion narrative",
            "start_date": date(2026, 2, 2),
            "status": "active documentation",
            "notes": "Demonstration infusion narrative emphasizing weekly monitoring expectations.",
        },
    )

    Encounter.objects.create(
        patient=sarah,
        encounter_type="imaging",
        date=date(2026, 4, 22),
        provider=alex,
        summary="CT staging encounter documentation · synthetic",
    )

    generate_source_backed_observations(sarah)
    generate_tumor_board_brief(sarah, user=alex)


def seed_michael_net(michael: Patient, alex: User, nurse: User):
    """Flagship pancreatic NET — Chromogranin trend, MEN1/Ki-67, MRI lesion language."""
    Observation.objects.filter(patient=michael).delete()
    EvidenceItem.objects.filter(patient=michael).delete()
    SourceBackedObservation.objects.filter(patient=michael).delete()
    DiagnosticReport.objects.filter(patient=michael).delete()
    ClinicalNote.objects.filter(patient=michael).delete()
    Treatment.objects.filter(patient=michael).delete()

    path = DiagnosticReport.objects.create(
        patient=michael,
        report_type="pathology",
        title="Pathology · NET wedge Ki-67",
        report_date=date(2026, 2, 18),
        uploaded_by=alex,
        raw_text=(
            "Pathology demonstrates well-differentiated pancreatic neuroendocrine neoplasm. "
            "Ki-67 index approximately 8%. Molecular summary notes MEN1 mutation detected in germline panel excerpt "
            "(research-use narrative only)."
        ),
        parse_status="parsed",
    )

    lab_jan = DiagnosticReport.objects.create(
        patient=michael,
        report_type="lab",
        title="Lab · Chromogranin A Jan",
        report_date=date(2026, 1, 20),
        uploaded_by=nurse,
        raw_text=(
            "Laboratory Report\nDate: 2026-01-20\nChromogranin A measured at 220 ng/mL, elevated from institutional ULN narrative."
        ),
        parse_status="parsed",
    )
    lab_feb = DiagnosticReport.objects.create(
        patient=michael,
        report_type="lab",
        title="Lab · Chromogranin A Feb",
        report_date=date(2026, 2, 15),
        uploaded_by=nurse,
        raw_text="Chromogranin A measured at 260 ng/mL on repeat sampling.",
        parse_status="parsed",
    )
    lab_mar = DiagnosticReport.objects.create(
        patient=michael,
        report_type="lab",
        title="Lab · Chromogranin A Mar",
        report_date=date(2026, 3, 12),
        uploaded_by=nurse,
        raw_text="Chromogranin A measured at 410 ng/mL, increased from prior value.",
        parse_status="parsed",
    )

    mri = DiagnosticReport.objects.create(
        patient=michael,
        report_type="imaging",
        title="MRI Abdomen · liver lesion follow-up",
        report_date=date(2026, 3, 26),
        uploaded_by=alex,
        raw_text=(
            "MRI Abdomen with contrast\nDate: 2026-03-26\n"
            "Findings: Stable dominant pancreatic body lesion with adjacent enhancing liver lesion "
            "recommended for continued correlation with biochemical markers and clinician review."
        ),
        parse_status="parsed",
    )

    note = DiagnosticReport.objects.create(
        patient=michael,
        report_type="oncology_note",
        title="Oncology visit · Everolimus tolerance",
        report_date=date(2026, 4, 4),
        uploaded_by=alex,
        raw_text=(
            "Patient reports fatigue while on everolimus; discusses appetite and diarrhea symptoms for monitoring. "
            "No autonomous therapy changes documented."
        ),
        parse_status="parsed",
    )

    _mk_obs_ev(
        michael,
        lab_jan,
        "tumor_marker",
        "Chromogranin A",
        220,
        "ng/mL",
        date(2026, 1, 20),
        "Chromogranin A 220 ng/mL",
        0.93,
        nurse,
    )
    _mk_obs_ev(
        michael,
        lab_feb,
        "tumor_marker",
        "Chromogranin A",
        260,
        "ng/mL",
        date(2026, 2, 15),
        "Chromogranin A 260 ng/mL",
        0.93,
        nurse,
    )
    _mk_obs_ev(
        michael,
        lab_mar,
        "tumor_marker",
        "Chromogranin A",
        410,
        "ng/mL",
        date(2026, 3, 12),
        "Chromogranin A 410 ng/mL",
        0.93,
        nurse,
    )

    Observation.objects.create(
        patient=michael,
        report=path,
        observation_type="biomarker",
        name="Ki-67 index",
        value_text="8%",
        observed_at=date(2026, 2, 18),
        source_snippet="Ki-67 index approximately 8% in pathology excerpt.",
        confidence=0.88,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )
    Observation.objects.create(
        patient=michael,
        report=path,
        observation_type="biomarker",
        name="MEN1",
        value_text="mutation mentioned",
        observed_at=date(2026, 2, 18),
        source_snippet="MEN1 mutation detected in documentation excerpt.",
        confidence=0.85,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Observation.objects.create(
        patient=michael,
        report=mri,
        observation_type="imaging_language",
        name="MRI lesion follow-up language",
        value_text="enhancing liver lesion language",
        source_snippet="Enhancing liver lesion recommended for correlation excerpt.",
        observed_at=date(2026, 3, 26),
        confidence=0.87,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Observation.objects.create(
        patient=michael,
        report=note,
        observation_type="symptom",
        name="Fatigue / GI symptom language",
        value_text="symptom documentation",
        source_snippet="Fatigue, appetite, diarrhea mentioned in clinic note excerpt.",
        confidence=0.8,
        observed_at=date(2026, 4, 4),
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Treatment.objects.create(
        patient=michael,
        name="Everolimus",
        treatment_type="Targeted therapy narrative",
        start_date=date(2026, 1, 8),
        status="active documentation",
        notes="Demonstration everolimus line with toxicity monitoring language.",
    )

    ClinicalNote.objects.create(
        patient=michael,
        author=nurse,
        note_type="follow_up",
        text="Phone triage for diarrhea symptoms — correlate with clinic documentation excerpts.",
        note_date=date(2026, 4, 6),
    )

    Encounter.objects.create(
        patient=michael,
        encounter_type="lab",
        date=date(2026, 3, 12),
        provider=nurse,
        summary="LAB encounter abstraction chromogranin cadence",
    )

    generate_source_backed_observations(michael)


def seed_crc_chart(p: Patient, alex: User, nurse: User):
    Observation.objects.filter(patient=p).delete()
    EvidenceItem.objects.filter(patient=p).delete()
    SourceBackedObservation.objects.filter(patient=p).delete()
    DiagnosticReport.objects.filter(patient=p).delete()
    ClinicalNote.objects.filter(patient=p).delete()
    Treatment.objects.filter(patient=p).delete()

    path = DiagnosticReport.objects.create(
        patient=p,
        report_type="pathology",
        title="Colon pathology · MSI noted",
        report_date=date(2026, 1, 8),
        uploaded_by=alex,
        raw_text="Immunohistochemistry comments reference MSI-high phenotype wording (documentation excerpt). KRAS wild-type narrative.",
        parse_status="parsed",
    )
    labs = [
        (
            date(2026, 2, 1),
            4.2,
            "Lab CEA baseline",
            "CEA measured at 4.2 ng/mL on surveillance labs.",
        ),
        (date(2026, 3, 4), 8.1, "Lab CEA rise", "CEA increased to 8.1 ng/mL."),
        (date(2026, 4, 2), 14.6, "Lab CEA continued rise", "CEA now 14.6 ng/mL."),
    ]
    lab_reports = []
    for d, val, title, txt in labs:
        r = DiagnosticReport.objects.create(
            patient=p,
            report_type="lab",
            title=title,
            report_date=d,
            uploaded_by=nurse,
            raw_text=f"Laboratory Report Date: {d.isoformat()}\n{txt}",
            parse_status="parsed",
        )
        lab_reports.append((r, d, val))

    ct = DiagnosticReport.objects.create(
        patient=p,
        report_type="imaging",
        title="CT chest/abdomen · hepatic lesions",
        report_date=date(2026, 4, 10),
        uploaded_by=alex,
        raw_text=(
            "CT Chest/Abdomen\nImpression: Interval increase in size of hepatic metastases compared with prior imaging. "
            "Clinical correlation recommended."
        ),
        parse_status="parsed",
    )

    note = DiagnosticReport.objects.create(
        patient=p,
        report_type="oncology_note",
        title="Oncology note · FOLFOX tolerance",
        report_date=date(2026, 4, 18),
        uploaded_by=alex,
        raw_text="Patient notes fatigue and decreased appetite; ongoing FOLFOX cycle documentation for clinician review.",
        parse_status="parsed",
    )

    for r, d, val in lab_reports:
        _mk_obs_ev(p, r, "tumor_marker", "CEA", val, "ng/mL", d, f"CEA {val} ng/mL excerpt", 0.9, nurse)

    Observation.objects.create(
        patient=p,
        report=path,
        observation_type="biomarker",
        name="MSI",
        value_text="MSI-high mentioned",
        observed_at=date(2026, 1, 8),
        source_snippet="MSI-high wording in pathology block.",
        confidence=0.82,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Observation.objects.create(
        patient=p,
        report=ct,
        observation_type="imaging_language",
        name="Liver metastasis language",
        value_text="imaging excerpt",
        observed_at=date(2026, 4, 10),
        source_snippet="Interval increase hepatic metastases excerpt.",
        confidence=0.88,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Treatment.objects.create(
        patient=p,
        name="FOLFOX",
        treatment_type="Chemotherapy",
        start_date=date(2026, 2, 15),
        status="active documentation",
        notes="Demonstration colorectal systemic regimen narrative.",
    )

    ClinicalNote.objects.create(
        patient=p,
        author=nurse,
        note_type="nursing",
        text="Patient educated on monitoring rectal bleeding symptoms — correlate clinically.",
        note_date=date(2026, 4, 20),
    )

    generate_source_backed_observations(p)


def seed_lung_chart(p: Patient, alex: User, nurse: User):
    Observation.objects.filter(patient=p).delete()
    EvidenceItem.objects.filter(patient=p).delete()
    SourceBackedObservation.objects.filter(patient=p).delete()
    DiagnosticReport.objects.filter(patient=p).delete()
    ClinicalNote.objects.filter(patient=p).delete()
    Treatment.objects.filter(patient=p).delete()

    path = DiagnosticReport.objects.create(
        patient=p,
        report_type="pathology",
        title="Biopsy · EGFR mutation documentation",
        report_date=date(2026, 2, 5),
        uploaded_by=alex,
        raw_text=(
            "Molecular pathology excerpt: EGFR exon 19 deletion detected. PD-L1 tumor proportion score 65% "
            "by immunohistochemistry narrative."
        ),
        parse_status="parsed",
    )

    DiagnosticReport.objects.create(
        patient=p,
        report_type="imaging",
        title="CT thorax · pulmonary nodule",
        report_date=date(2026, 3, 1),
        uploaded_by=alex,
        raw_text="CT Thorax: Pulmonary nodule with recommendation for continued surveillance correlation.",
        parse_status="parsed",
    )
    ct2 = DiagnosticReport.objects.create(
        patient=p,
        report_type="imaging",
        title="MRI brain · metastasis screening",
        report_date=date(2026, 4, 2),
        uploaded_by=alex,
        raw_text=(
            "MRI Brain: New enhancing lesion concerning for metastatic disease — correlation with neurology "
            "and oncology documentation requested."
        ),
        parse_status="parsed",
    )

    note = DiagnosticReport.objects.create(
        patient=p,
        report_type="oncology_note",
        title="Oncology · pembrolizumab discussion",
        report_date=date(2026, 4, 12),
        uploaded_by=nurse,
        raw_text=(
            "Discussed cough and dyspnea symptoms; pembrolizumab continuation per treating team documentation excerpt."
        ),
        parse_status="parsed",
    )

    Observation.objects.create(
        patient=p,
        report=path,
        observation_type="biomarker",
        name="EGFR",
        value_text="exon 19 del",
        observed_at=date(2026, 2, 5),
        source_snippet="EGFR exon 19 deletion excerpt.",
        confidence=0.9,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )
    Observation.objects.create(
        patient=p,
        report=path,
        observation_type="biomarker",
        name="PD-L1",
        value_text="65%",
        observed_at=date(2026, 2, 5),
        source_snippet="PD-L1 TPS 65% excerpt.",
        confidence=0.88,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Observation.objects.create(
        patient=p,
        report=ct2,
        observation_type="imaging_language",
        name="Brain lesion language",
        value_text="documentation excerpt",
        observed_at=date(2026, 4, 2),
        source_snippet="New enhancing lesion metastatic disease wording excerpt.",
        confidence=0.86,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Treatment.objects.create(
        patient=p,
        name="Pembrolizumab",
        treatment_type="Immunotherapy",
        start_date=date(2026, 3, 10),
        status="active documentation",
        notes="Demonstration IO regimen narrative.",
    )

    ClinicalNote.objects.create(
        patient=p,
        author=nurse,
        note_type="visit",
        text="Symptom review cough dyspnea — documented for clinician correlation.",
        note_date=date(2026, 4, 14),
    )

    generate_source_backed_observations(p)


def seed_breast_chart(p: Patient, alex: User, nurse: User):
    Observation.objects.filter(patient=p).delete()
    EvidenceItem.objects.filter(patient=p).delete()
    SourceBackedObservation.objects.filter(patient=p).delete()
    DiagnosticReport.objects.filter(patient=p).delete()
    ClinicalNote.objects.filter(patient=p).delete()
    Treatment.objects.filter(patient=p).delete()

    path = DiagnosticReport.objects.create(
        patient=p,
        report_type="pathology",
        title="Breast pathology · HER2 amplification",
        report_date=date(2026, 1, 25),
        uploaded_by=alex,
        raw_text=(
            "Invasive ductal carcinoma. HER2 positive by IHC narrative. "
            "Estrogen receptor weak positivity mentioned in synoptic excerpt."
        ),
        parse_status="parsed",
    )

    labs = [
        (date(2026, 2, 10), 28.0),
        (date(2026, 3, 11), 41.0),
        (date(2026, 4, 9), 56.0),
    ]
    lr = []
    for d, val in labs:
        lr.append(
            DiagnosticReport.objects.create(
                patient=p,
                report_type="lab",
                title=f"Lab CA 15-3 · {d.isoformat()}",
                report_date=d,
                uploaded_by=nurse,
                raw_text=f"Laboratory Report Date: {d.isoformat()}\nCA 15-3 measured at {val} U/mL.",
                parse_status="parsed",
            )
        )

    mri = DiagnosticReport.objects.create(
        patient=p,
        report_type="imaging",
        title="MRI spine · bone lesion survey",
        report_date=date(2026, 4, 5),
        uploaded_by=alex,
        raw_text="MRI Spine: Bone lesion with interval increase wording — correlate with oncology team.",
        parse_status="parsed",
    )

    note = DiagnosticReport.objects.create(
        patient=p,
        report_type="oncology_note",
        title="Oncology · trastuzumab visit",
        report_date=date(2026, 4, 16),
        uploaded_by=alex,
        raw_text="Patient reports fatigue and bone pain; trastuzumab continuation documented for clinician review.",
        parse_status="parsed",
    )

    for i, (d, val) in enumerate(labs):
        _mk_obs_ev(
            p,
            lr[i],
            "tumor_marker",
            "CA 15-3",
            val,
            "U/mL",
            d,
            f"CA 15-3 {val} U/mL excerpt",
            0.91,
            nurse,
        )

    Observation.objects.create(
        patient=p,
        report=path,
        observation_type="biomarker",
        name="HER2",
        value_text="positive",
        observed_at=date(2026, 1, 25),
        source_snippet="HER2 positive excerpt.",
        confidence=0.9,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Observation.objects.create(
        patient=p,
        report=mri,
        observation_type="imaging_language",
        name="Bone lesion language",
        value_text="interval increase",
        observed_at=date(2026, 4, 5),
        source_snippet="Bone lesion interval increase excerpt.",
        confidence=0.85,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Treatment.objects.create(
        patient=p,
        name="Trastuzumab",
        treatment_type="Targeted therapy",
        start_date=date(2026, 2, 5),
        status="active documentation",
        notes="Demonstration HER2-directed regimen narrative.",
    )

    ClinicalNote.objects.create(
        patient=p,
        author=nurse,
        note_type="nursing",
        text="Education materials provided regarding fatigue monitoring.",
        note_date=date(2026, 4, 18),
    )

    generate_source_backed_observations(p)


def seed_pancreatic_adc_rich(p: Patient, alex: User, nurse: User, *, rising_ca19: bool):
    """Generic PDAC-style chart with variable CA 19-9 story."""
    Observation.objects.filter(patient=p).delete()
    EvidenceItem.objects.filter(patient=p).delete()
    SourceBackedObservation.objects.filter(patient=p).delete()
    DiagnosticReport.objects.filter(patient=p).delete()
    ClinicalNote.objects.filter(patient=p).delete()
    Treatment.objects.filter(patient=p).delete()

    path = DiagnosticReport.objects.create(
        patient=p,
        report_type="pathology",
        title="Pathology · KRAS documentation",
        report_date=date(2026, 1, 5),
        uploaded_by=alex,
        raw_text="Pathology excerpt references KRAS mutation nomenclature for institutional reporting.",
        parse_status="parsed",
    )

    dates_vals = (
        [(date(2026, 2, 1), 85), (date(2026, 3, 2), 112), (date(2026, 4, 1), 148)]
        if not rising_ca19
        else [(date(2026, 2, 1), 200), (date(2026, 3, 3), 340), (date(2026, 4, 4), 520)]
    )

    lab_reports = []
    for d, val in dates_vals:
        lab_reports.append(
            DiagnosticReport.objects.create(
                patient=p,
                report_type="lab",
                title=f"Lab CA19-9 · {d.isoformat()}",
                report_date=d,
                uploaded_by=nurse,
                raw_text=(
                    f"Laboratory Report Date: {d.isoformat()}\nCA 19-9 measured at {val} U/mL.\n"
                    f"Total bilirubin 0.9 mg/dL."
                ),
                parse_status="parsed",
            )
        )

    img = DiagnosticReport.objects.create(
        patient=p,
        report_type="imaging",
        title="CT abdomen · lesion surveillance",
        report_date=date(2026, 4, 8),
        uploaded_by=alex,
        raw_text=(
            "CT Abdomen: Pancreatic head lesion with liver lesion correlation language; interval increase "
            "noted compared with prior study excerpt."
        ),
        parse_status="parsed",
    )

    onco = DiagnosticReport.objects.create(
        patient=p,
        report_type="oncology_note",
        title="Oncology clinic note",
        report_date=date(2026, 4, 20),
        uploaded_by=alex,
        raw_text="Patient reports fatigue and abdominal pain for clinician correlation; gemcitabine discussion excerpt.",
        parse_status="parsed",
    )

    for i, (d, val) in enumerate(dates_vals):
        _mk_obs_ev(
            p,
            lab_reports[i],
            "tumor_marker",
            "CA 19-9",
            float(val),
            "U/mL",
            d,
            f"CA 19-9 {val} U/mL",
            0.92,
            alex,
        )

    Observation.objects.create(
        patient=p,
        report=img,
        observation_type="imaging_language",
        name="Lesion surveillance language",
        value_text="excerpt",
        observed_at=date(2026, 4, 8),
        source_snippet="Interval increase pancreatic/liver lesion excerpt.",
        confidence=0.86,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )

    Treatment.objects.create(
        patient=p,
        name=p.current_treatment or "Systemic therapy narrative",
        treatment_type="Chemotherapy narrative",
        start_date=date(2026, 2, 1),
        status="active documentation",
        notes="Synthetic treatment line for chart completeness demo.",
    )

    ClinicalNote.objects.create(
        patient=p,
        author=nurse,
        note_type="visit",
        text="Phone check regarding nausea symptoms — correlate with clinic visits.",
        note_date=date(2026, 4, 22),
    )

    for adjunct in range(3):
        d = date(2026, 4, 10) + timedelta(days=adjunct * 5)
        DiagnosticReport.objects.create(
            patient=p,
            report_type="lab",
            title=f"Adjunct lab trace · MRN {p.medical_record_number} · {d.isoformat()}",
            report_date=d,
            uploaded_by=nurse,
            raw_text=(
                f"Laboratory batch {d.isoformat()}: albumin documented; hepatic enzymes listed for clinician review excerpt; "
                "CA 19-9 contextual comment references prior trend language only."
            ),
            parse_status="parsed",
        )
        ClinicalNote.objects.create(
            patient=p,
            author=nurse,
            note_type="phone",
            text=f"Triage documentation {d.isoformat()}: reinforces appetite and nausea wording already in clinic notes.",
            note_date=d,
        )

    generate_source_backed_observations(p)


def seed_light_chart(p: Patient, alex: User):
    """Minimal surveillance-style chart (e.g. cystic lesion patient)."""
    Observation.objects.filter(patient=p).delete()
    EvidenceItem.objects.filter(patient=p).delete()
    SourceBackedObservation.objects.filter(patient=p).delete()
    DiagnosticReport.objects.filter(patient=p).delete()
    ClinicalNote.objects.filter(patient=p).delete()
    Treatment.objects.filter(patient=p).delete()

    r = DiagnosticReport.objects.create(
        patient=p,
        report_type="imaging",
        title="MRI surveillance · stable cyst",
        report_date=date(2026, 3, 15),
        uploaded_by=alex,
        raw_text="MRI: Pancreatic cystic lesion stable without interval increase wording in this excerpt.",
        parse_status="parsed",
    )

    ClinicalNote.objects.create(
        patient=p,
        author=alex,
        note_type="follow_up",
        text="Routine surveillance discussion — no new symptom documentation in this excerpt.",
        note_date=date(2026, 4, 1),
    )

    DiagnosticReport.objects.create(
        patient=p,
        report_type="imaging",
        title="MRI pancreas surveillance · secondary pass",
        report_date=date(2026, 4, 18),
        uploaded_by=alex,
        raw_text=(
            "MRI excerpt: pancreatic cyst morphology stable; no aggressive imaging descriptor language surfaced in synthetic block."
        ),
        parse_status="parsed",
    )
    DiagnosticReport.objects.create(
        patient=p,
        report_type="oncology_note",
        title="Navigator touchpoint · surveillance only",
        report_date=date(2026, 4, 25),
        uploaded_by=alex,
        raw_text="Navigator note reinforces continued imaging cadence without new toxicity language.",
        parse_status="parsed",
    )
    ClinicalNote.objects.create(
        patient=p,
        author=alex,
        note_type="phone",
        text="Annual reminder call documented — patient denies new red-flag symptoms per triage script.",
        note_date=date(2026, 4, 26),
    )

    generate_source_backed_observations(p)


def seed_general_oncology_chart(p: Patient, alex: User, nurse: User):
    """Non-profile flagship chart — biomarker + symptom language for general profile."""
    Observation.objects.filter(patient=p).delete()
    EvidenceItem.objects.filter(patient=p).delete()
    SourceBackedObservation.objects.filter(patient=p).delete()
    DiagnosticReport.objects.filter(patient=p).delete()
    ClinicalNote.objects.filter(patient=p).delete()
    Treatment.objects.filter(patient=p).delete()

    r = DiagnosticReport.objects.create(
        patient=p,
        report_type="oncology_note",
        title="Oncology intake excerpt",
        report_date=date(2026, 3, 20),
        uploaded_by=alex,
        raw_text=(
            "Consult note excerpt: discusses KRAS documentation from outside records and fatigue symptoms "
            "for clinician correlation."
        ),
        parse_status="parsed",
    )
    Observation.objects.create(
        patient=p,
        report=r,
        observation_type="biomarker",
        name="KRAS",
        value_text="mentioned in records",
        observed_at=date(2026, 3, 20),
        source_snippet="KRAS mentioned in consult excerpt.",
        confidence=0.8,
        confirmation_status="confirmed",
        confirmed_by=alex,
    )
    ClinicalNote.objects.create(
        patient=p,
        author=nurse,
        note_type="visit",
        text="Patient reports nausea — monitoring per clinic protocol excerpt.",
        note_date=date(2026, 4, 2),
    )
    Treatment.objects.create(
        patient=p,
        name="Chemotherapy narrative",
        treatment_type="Systemic",
        start_date=date(2026, 3, 1),
        status="active documentation",
        notes="Synthetic general oncology treatment placeholder.",
    )
    generate_source_backed_observations(p)
