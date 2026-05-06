"""
Cancer-type-aware vocabularies for parsing, rules, and search boosting — prototype only, not clinical guidance.
"""
from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class MissingDataCheck(TypedDict, total=False):
    observation_name_contains: str
    window_days: int
    requires_active_treatment: bool
    title: str


class CancerProfile(TypedDict):
    id: str
    tumor_markers: List[str]
    labs: List[str]
    biomarkers: List[str]
    treatments: List[str]
    symptoms: List[str]
    imaging_terms: List[str]
    missing_data_checks: List[MissingDataCheck]
    search_seed_terms: List[str]


CANCER_ANALYSIS_CONFIG: Dict[str, CancerProfile] = {
    "pancreatic_adenocarcinoma": {
        "id": "pancreatic_adenocarcinoma",
        "tumor_markers": ["CA 19-9", "CA19-9"],
        "labs": ["bilirubin", "albumin", "AST", "ALT", "alkaline phosphatase"],
        "biomarkers": ["KRAS", "TP53", "SMAD4", "CDKN2A", "BRCA1", "BRCA2"],
        "treatments": ["FOLFIRINOX", "gemcitabine", "nab-paclitaxel", "Whipple", "radiation"],
        "symptoms": ["fatigue", "weight loss", "lost weight", "jaundice", "abdominal pain", "appetite loss", "nausea"],
        "imaging_terms": [
            "interval increase",
            "increased lesion size",
            "progression",
            "new lesion",
            "metastatic disease",
            "pancreatic head lesion",
            "liver lesion",
            "biliary obstruction",
            "suspicious for",
            "concerning for",
            "worsening",
        ],
        "missing_data_checks": [
            {
                "observation_name_contains": "bilirubin",
                "window_days": 30,
                "requires_active_treatment": True,
                "title": "Recent bilirubin observation missing",
            },
        ],
        "search_seed_terms": [
            "Rising CA 19-9",
            "KRAS",
            "Missing bilirubin",
            "FOLFIRINOX",
            "Weight loss",
            "Pancreatic head lesion",
        ],
    },
    "pancreatic_neuroendocrine_tumor": {
        "id": "pancreatic_neuroendocrine_tumor",
        "tumor_markers": ["Chromogranin A", "chromogranin", "CgA"],
        "labs": ["glucose", "insulin", "gastrin"],
        "biomarkers": ["MEN1", "DAXX", "ATRX", "Ki-67", "Ki67"],
        "treatments": ["everolimus", "sunitinib", "octreotide", "lanreotide", "somatostatin"],
        "symptoms": ["flushing", "diarrhea", "hypoglycemia", "fatigue", "weight loss", "abdominal pain"],
        "imaging_terms": [
            "mri",
            "magnetic resonance",
            "liver lesion",
            "enhancing lesion",
            "interval increase",
            "new lesion",
            "somatostatin receptor",
            "progression",
            "metastatic disease",
        ],
        "missing_data_checks": [
            {
                "observation_name_contains": "chromogranin",
                "window_days": 90,
                "requires_active_treatment": False,
                "title": "Recent Chromogranin A assessment missing",
            },
        ],
        "search_seed_terms": [
            "Chromogranin A",
            "MEN1",
            "Ki-67",
            "Everolimus",
            "Liver lesion",
            "Flushing",
        ],
    },
    "colorectal_cancer": {
        "id": "colorectal_cancer",
        "tumor_markers": ["CEA", "carcinoembryonic"],
        "labs": ["hemoglobin", "CEA", "albumin", "CRP"],
        "biomarkers": ["KRAS", "NRAS", "BRAF", "MSI", "MMR", "HER2"],
        "treatments": ["FOLFOX", "FOLFIRI", "bevacizumab", "cetuximab", "capecitabine", "oxaliplatin"],
        "symptoms": ["rectal bleeding", "weight loss", "fatigue", "abdominal pain", "bowel habit change", "nausea"],
        "imaging_terms": [
            "liver lesion",
            "interval increase",
            "new lesion",
            "metastatic disease",
            "progression",
            "lymph node",
        ],
        "missing_data_checks": [
            {
                "observation_name_contains": "CEA",
                "window_days": 60,
                "requires_active_treatment": False,
                "title": "Recent CEA tumor marker assessment missing",
            },
        ],
        "search_seed_terms": ["CEA trend", "KRAS", "MSI", "FOLFOX", "Liver metastasis", "Rectal bleeding"],
    },
    "lung_adenocarcinoma": {
        "id": "lung_adenocarcinoma",
        "tumor_markers": [],
        "labs": ["calcium", "albumin", "LDH"],
        "biomarkers": ["EGFR", "ALK", "ROS1", "PD-L1", "KRAS", "BRAF"],
        "treatments": ["osimertinib", "pembrolizumab", "chemotherapy", "radiation", "carboplatin", "pemetrexed"],
        "symptoms": ["cough", "dyspnea", "fatigue", "weight loss", "chest pain", "hemoptysis"],
        "imaging_terms": [
            "interval increase",
            "new lesion",
            "brain metastasis",
            "progression",
            "pulmonary nodule",
            "pleural effusion",
        ],
        "missing_data_checks": [],
        "search_seed_terms": ["EGFR", "PD-L1", "ALK", "Brain metastases", "Pembrolizumab", "Osimertinib"],
    },
    "breast_cancer": {
        "id": "breast_cancer",
        "tumor_markers": ["CA 15-3", "CA15-3"],
        "labs": ["CA 15-3", "hemoglobin", "alkaline phosphatase"],
        "biomarkers": ["HER2", "BRCA1", "BRCA2", "Ki-67", "estrogen receptor", "progesterone receptor"],
        "treatments": ["trastuzumab", "pertuzumab", "tamoxifen", "letrozole", "palbociclib", "chemotherapy"],
        "symptoms": ["fatigue", "weight loss", "bone pain", "nausea"],
        "imaging_terms": [
            "interval increase",
            "bone lesion",
            "liver lesion",
            "progression",
            "new lesion",
            "metastatic disease",
        ],
        "missing_data_checks": [
            {
                "observation_name_contains": "CA 15-3",
                "window_days": 90,
                "requires_active_treatment": False,
                "title": "Recent CA 15-3 assessment missing",
            },
        ],
        "search_seed_terms": ["HER2", "ER PR", "CA 15-3", "Trastuzumab", "BRCA", "Bone metastasis"],
    },
    "general_oncology": {
        "id": "general_oncology",
        "tumor_markers": ["CA 19-9", "CEA", "Chromogranin A"],
        "labs": ["albumin", "bilirubin", "hemoglobin"],
        "biomarkers": ["KRAS", "TP53"],
        "treatments": ["chemotherapy", "radiation", "clinical trial"],
        "symptoms": ["fatigue", "weight loss", "pain", "nausea", "appetite"],
        "imaging_terms": [
            "interval increase",
            "new lesion",
            "progression",
            "metastatic disease",
            "worsening",
        ],
        "missing_data_checks": [],
        "search_seed_terms": ["Fatigue", "Tumor marker", "Imaging follow-up", "Biopsy", "Treatment tolerance"],
    },
}


def _dx_key(primary_diagnosis: str) -> str:
    return (primary_diagnosis or "").lower()


def get_profile_for_parse(report) -> CancerProfile:
    """Profile for parser when report may omit patient (e.g. tests use SimpleNamespace)."""
    p = getattr(report, "patient", None)
    if p is None:
        return CANCER_ANALYSIS_CONFIG["general_oncology"]
    return get_cancer_profile(p)


def get_cancer_profile(patient) -> CancerProfile:
    """Return the closest matching analysis profile from patient.primary_diagnosis."""
    dx = _dx_key(getattr(patient, "primary_diagnosis", "") or "")

    if "neuroendocrine" in dx or "pancreatic net" in dx:
        return CANCER_ANALYSIS_CONFIG["pancreatic_neuroendocrine_tumor"]

    if any(
        k in dx
        for k in (
            "colorectal",
            "colon cancer",
            "rectal",
            "crc",
        )
    ):
        return CANCER_ANALYSIS_CONFIG["colorectal_cancer"]

    if any(
        k in dx
        for k in (
            "lung",
            "pulmonary adenocarcinoma",
            "nsclc",
            "non-small cell",
        )
    ):
        return CANCER_ANALYSIS_CONFIG["lung_adenocarcinoma"]

    if "breast" in dx:
        return CANCER_ANALYSIS_CONFIG["breast_cancer"]

    if any(
        k in dx
        for k in (
            "pancreatic adenocarcinoma",
            "pancreatic ductal",
            "pdac",
            "pancreatic cancer",
            "pancreatic head mass",
            "pancreatic cystic",
            "whipple",
            "pancreatoduodenectomy",
            "metastatic pancreatic",
        )
    ):
        if "neuroendocrine" in dx:
            return CANCER_ANALYSIS_CONFIG["pancreatic_neuroendocrine_tumor"]
        return CANCER_ANALYSIS_CONFIG["pancreatic_adenocarcinoma"]

    return CANCER_ANALYSIS_CONFIG["general_oncology"]


def profile_vocabulary_flat(profile: CancerProfile) -> List[str]:
    """Terms used for search rank boosting when patient scope is set."""
    out: List[str] = []
    for key in ("tumor_markers", "labs", "biomarkers", "treatments", "symptoms", "imaging_terms"):
        out.extend(profile.get(key, []) if isinstance(profile.get(key), list) else [])
    return [t.lower() for t in out if t]
