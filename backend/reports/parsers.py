"""
Rule-based oncology report extraction. Not clinical decision support — language detection only.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List

from evidence.cancer_profiles import get_profile_for_parse


def parse_report_text(report) -> Dict[str, Any]:
    """Return extraction buckets for a DiagnosticReport."""
    raw = (report.raw_text or "").strip()
    lowered = raw.lower()
    profile = get_profile_for_parse(report)

    labs: List[Dict[str, Any]] = []
    biomarkers: List[Dict[str, Any]] = []
    symptoms: List[Dict[str, Any]] = []
    imaging_language: List[Dict[str, Any]] = []
    treatments: List[Dict[str, Any]] = []

    def add_lab(name: str, value_number: float | None, unit: str, snippet: str, conf: float):
        labs.append(
            {
                "name": name,
                "value_number": value_number,
                "unit": unit,
                "snippet": snippet.strip()[:400],
                "confidence": conf,
            }
        )

    # CA 19-9
    ca_pattern = re.compile(
        r"CA\s*19[-\s]?9[^\d]{0,48}(\d+(?:\.\d+)?)\s*(U/mL|units/?mL|U/ml)?",
        re.IGNORECASE,
    )
    for m in ca_pattern.finditer(raw):
        add_lab("CA 19-9", float(m.group(1)), (m.group(2) or "U/mL").replace("u", "U"), m.group(0), 0.92)

    # Chromogranin A (NET)
    cg_pat = re.compile(
        r"(?:chromogranin\s*a|\bcga\b)[^\d]{0,32}(\d+(?:\.\d+)?)\s*(ng/mL|ng/ml|µg/L|ug/L)?",
        re.IGNORECASE,
    )
    for m in cg_pat.finditer(raw):
        add_lab(
            "Chromogranin A",
            float(m.group(1)),
            (m.group(2) or "ng/mL").replace("u", "µ"),
            m.group(0),
            0.9,
        )

    # CEA (colorectal)
    cea_pat = re.compile(
        r"\bCEA\b[^\d]{0,36}(\d+(?:\.\d+)?)\s*(ng/mL|ng/ml|µg/L|ug/L)?",
        re.IGNORECASE,
    )
    for m in cea_pat.finditer(raw):
        add_lab("CEA", float(m.group(1)), (m.group(2) or "ng/mL"), m.group(0), 0.89)

    # CA 15-3 (breast)
    ca153_pat = re.compile(
        r"CA\s*15[-\s]?3[^\d]{0,48}(\d+(?:\.\d+)?)\s*(U/mL|units/?mL|U/ml)?",
        re.IGNORECASE,
    )
    for m in ca153_pat.finditer(raw):
        add_lab("CA 15-3", float(m.group(1)), (m.group(2) or "U/mL").replace("u", "U"), m.group(0), 0.88)

    # Common labs
    lab_patterns = [
        (r"total\s+bilirubin[^\d]{0,10}(\d+(?:\.\d+)?)\s*(mg/dL)?", "Bilirubin", "mg/dL", 0.88),
        (r"bilirubin[^\d]{0,10}(\d+(?:\.\d+)?)\s*(mg/dL)?", "Bilirubin", "mg/dL", 0.85),
        (r"albumin[^\d]{0,10}(\d+(?:\.\d+)?)\s*(g/dL)?", "Albumin", "g/dL", 0.85),
        (
            r"alkaline\s+phosphatase[^\d]{0,8}(\d+(?:\.\d+)?)\s*(U/L|IU/L)?",
            "Alkaline phosphatase",
            "U/L",
            0.84,
        ),
        (r"\bAST\b[^\d]{0,8}(\d+(?:\.\d+)?)\s*(U/L|IU/L)?", "AST", "U/L", 0.83),
        (r"\bALT\b[^\d]{0,8}(\d+(?:\.\d+)?)\s*(U/L|IU/L)?", "ALT", "U/L", 0.83),
        (r"hemoglobin[^\d]{0,10}(\d+(?:\.\d+)?)\s*(g/dL)?", "Hemoglobin", "g/dL", 0.84),
        (r"\bWBC\b[^\d]{0,10}(\d+(?:\.\d+)?)\s*(K/uL|x10\^9/L)?", "WBC", "K/uL", 0.8),
        (r"platelet[^\d]{0,12}(\d+(?:\.\d+)?)\s*(K/uL|x10\^9/L)?", "Platelet count", "K/uL", 0.78),
        (r"\bLDH\b[^\d]{0,10}(\d+(?:\.\d+)?)\s*(U/L|IU/L)?", "LDH", "U/L", 0.82),
    ]
    for pattern, name, unit, conf in lab_patterns:
        for m in re.finditer(pattern, raw, re.IGNORECASE):
            try:
                val = float(m.group(1))
            except (TypeError, ValueError):
                continue
            u = m.group(2) or unit
            add_lab(name, val, u, m.group(0), conf)

    # Weight
    wt_pattern = re.compile(
        r"(?:weight|wt)\s*(?:of|:|is|was|decreased to|increased to)?\s*(\d+(?:\.\d+)?)\s*kg",
        re.IGNORECASE,
    )
    for m in wt_pattern.finditer(raw):
        labs.append(
            {
                "name": "Weight",
                "value_number": float(m.group(1)),
                "unit": "kg",
                "snippet": m.group(0).strip()[:400],
                "confidence": 0.86,
            }
        )

    bio_terms = [
        ("KRAS G12D", r"KRAS\s+G12D"),
        ("KRAS", r"\bKRAS\b"),
        ("TP53", r"\bTP53\b"),
        ("SMAD4", r"\bSMAD4\b"),
        ("CDKN2A", r"\bCDKN2A\b"),
        ("BRCA1", r"\bBRCA1\b"),
        ("BRCA2", r"\bBRCA2\b"),
        ("MSI", r"\bMSI\b"),
        ("MMR", r"\bMMR\b"),
        ("NRAS", r"\bNRAS\b"),
        ("BRAF", r"\bBRAF\b"),
        ("EGFR", r"\bEGFR\b"),
        ("ALK", r"\bALK\b"),
        ("ROS1", r"\bROS1\b"),
        ("PD-L1", r"PD[- ]?L1"),
        ("MEN1", r"\bMEN1\b"),
        ("DAXX", r"\bDAXX\b"),
        ("ATRX", r"\bATRX\b"),
        ("Ki-67", r"Ki[- ]?67"),
        ("HER2", r"\bHER2\b"),
    ]
    bio_seen = set()

    def add_bio(label: str, snippet: str, conf: float):
        if label in bio_seen:
            return
        bio_seen.add(label)
        biomarkers.append({"name": label, "value_text": label, "snippet": snippet[:400], "confidence": conf})

    for label, pat in bio_terms:
        for m in re.finditer(pat, raw, re.IGNORECASE):
            add_bio(label, _line_context(raw, m.start()), 0.82 if label != "KRAS G12D" else 0.9)
            break

    for bio in profile.get("biomarkers") or []:
        if bio in bio_seen:
            continue
        try:
            pat = r"\b" + re.escape(bio) + r"\b"
        except re.error:
            continue
        for m in re.finditer(pat, raw, re.IGNORECASE):
            add_bio(bio, _line_context(raw, m.start()), 0.81)
            break

    treatment_keywords = [
        "FOLFIRINOX",
        "FOLFOX",
        "FOLFIRI",
        "Gemcitabine",
        "nab-paclitaxel",
        "paclitaxel",
        "radiation",
        "Whipple",
        "biopsy",
        "surgery",
        "Everolimus",
        "sunitinib",
        "octreotide",
        "lanreotide",
        "bevacizumab",
        "cetuximab",
        "capecitabine",
        "oxaliplatin",
        "osimertinib",
        "pembrolizumab",
        "carboplatin",
        "pemetrexed",
        "trastuzumab",
        "pertuzumab",
        "tamoxifen",
        "letrozole",
        "palbociclib",
        "clinical trial",
    ]
    treatment_keywords.extend(profile.get("treatments") or [])
    low_raw = lowered
    tx_seen = set()
    for term in treatment_keywords:
        tl = term.lower()
        if tl in tx_seen:
            continue
        tx_seen.add(tl)
        idx = low_raw.find(tl)
        if idx != -1:
            snippet = _line_context(raw, idx)
            treatments.append({"name": term, "snippet": snippet, "confidence": 0.8})

    symptom_map = [
        ("fatigue", r"fatigue"),
        ("weight loss", r"(weight\s+loss|lost\s+weight)"),
        ("abdominal pain", r"abdominal\s+pain"),
        ("jaundice", r"jaundice"),
        ("nausea", r"nausea"),
        ("appetite loss", r"(appetite\s+loss|decreased\s+appetite|poor\s+appetite)"),
        ("flushing", r"flushing"),
        ("diarrhea", r"diarrhea"),
        ("cough", r"\bcough\b"),
        ("dyspnea", r"dyspnea"),
        ("hemoptysis", r"hemoptysis"),
        ("rectal bleeding", r"rectal\s+bleeding"),
    ]
    sym_seen = set()
    for name, pat in symptom_map:
        m = re.search(pat, lowered)
        if m:
            sym_seen.add(name.lower())
            snippet = _line_context(raw, m.start())
            symptoms.append({"name": name, "snippet": snippet, "confidence": 0.79})

    for s in profile.get("symptoms") or []:
        sl = s.lower()
        if sl in sym_seen:
            continue
        if sl in lowered:
            sym_seen.add(sl)
            idx = lowered.index(sl)
            snippet = _line_context(raw, idx)
            symptoms.append({"name": s, "snippet": snippet, "confidence": 0.78})

    prog_terms = [
        "interval increase",
        "increased lesion size",
        "progression",
        "worsening",
        "new lesion",
        "metastatic disease",
        "suspicious for",
        "concerning for",
        "pancreatic head lesion",
        "liver lesion",
        "biliary obstruction",
        "pulmonary nodule",
        "brain metastasis",
        "bone lesion",
        "enhancing lesion",
        "somatostatin receptor",
    ]
    for t in profile.get("imaging_terms") or []:
        tl = t.lower()
        if tl not in prog_terms:
            prog_terms.append(tl)

    img_seen = set()
    for term in prog_terms:
        tl = term.lower()
        if tl in img_seen:
            continue
        if tl in lowered:
            img_seen.add(tl)
            idx = lowered.index(tl)
            snippet = _line_context(raw, idx)
            imaging_language.append({"name": term, "snippet": snippet, "confidence": 0.81})

    metadata: Dict[str, Any] = {
        "report_type": getattr(report, "report_type", None),
        "cancer_profile_id": profile.get("id"),
    }
    if getattr(report, "report_date", None):
        metadata["report_date"] = report.report_date.isoformat()
    else:
        inferred = infer_date_from_text(raw)
        if inferred:
            metadata["report_date"] = inferred.isoformat()

    return {
        "metadata": metadata,
        "labs": labs,
        "biomarkers": biomarkers,
        "symptoms": symptoms,
        "imaging_language": imaging_language,
        "treatments": treatments,
    }


def infer_date_from_text(text: str) -> date | None:
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m2 = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m2:
        return date(int(m2.group(3)), int(m2.group(1)), int(m2.group(2)))
    return None


def _line_context(raw: str, idx: int, window: int = 180) -> str:
    start = max(raw.rfind("\n", 0, idx), idx - window)
    end = min(raw.find("\n", idx), idx + window)
    if end == -1:
        end = min(len(raw), idx + window)
    return raw[start:end].strip().replace("\n", " ")[:400]
