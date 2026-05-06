"""Synthetic oncology dataset for prototyping — never PHI."""

from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import UserProfile
from core.seed_demo import (
    seed_breast_chart,
    seed_condition_encounter,
    seed_crc_chart,
    seed_general_oncology_chart,
    seed_light_chart,
    seed_lung_chart,
    seed_michael_net,
    seed_pancreatic_adc_rich,
    seed_sarah_flagship,
)
from evidence.models import Observation, SourceBackedObservation
from evidence.services import generate_source_backed_observations
from patients.models import Patient
from reports.models import DiagnosticReport


DEMO_USERNAMES = ("alex.morgan.demo", "jamie.lee.demo", "priya.shah.demo")
DEMO_MRNS = (
    "1058846",
    "1042201",
    "1042202",
    "1042203",
    "1042204",
    "1042205",
    "1042206",
    "1042207",
    "1042208",
    "1042209",
    "1042210",
    "1042211",
    "1042212",
    "1042213",
    "1042214",
    "1042215",
    "1042216",
    "1042217",
    "1042218",
    "1042219",
    "1042220",
    "1042221",
    "1042222",
    "1042223",
    "1042224",
    "1042225",
    "1042226",
    "1042227",
    "1042228",
    "1042229",
    "1042230",
    "1042231",
    "1042232",
    "1042233",
    "1042234",
)


class Command(BaseCommand):
    help = "Load synthetic multi-tumor demo patients and staff logins."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Rebuilding deterministic demo corpus..."))

        User.objects.filter(username__in=DEMO_USERNAMES).delete()
        Patient.objects.filter(medical_record_number__in=DEMO_MRNS).delete()

        alex = User.objects.create_user(
            username="alex.morgan.demo",
            password="password123",
            email="alex@oncolens.demo",
            first_name="Alex",
            last_name="Morgan",
            is_staff=True,
        )

        nurse = User.objects.create_user(
            username="jamie.lee.demo",
            password="password123",
            email="jamie@oncolens.demo",
            first_name="Jamie",
            last_name="Lee",
        )

        admin = User.objects.create_user(
            username="priya.shah.demo",
            password="password123",
            email="priya@oncolens.demo",
            first_name="Priya",
            last_name="Shah",
            is_staff=True,
            is_superuser=True,
        )

        UserProfile.objects.filter(user__in=[alex, nurse, admin]).delete()
        UserProfile.objects.create(user=alex, role="doctor", title="Medical Oncologist", avatar_initials="AM")
        UserProfile.objects.create(user=nurse, role="nurse", title="Clinical Nurse Navigator", avatar_initials="JL")
        UserProfile.objects.create(user=admin, role="admin", title="Operations Admin", avatar_initials="PS")

        specs = [
            ("1058846", "Sarah", "Johnson", date(1964, 2, 14), "F", "Pancreatic adenocarcinoma", "Stage III", "FOLFIRINOX", "needs_review", "sarah"),
            ("1042201", "Michael", "Chen", date(1971, 5, 2), "M", "Pancreatic neuroendocrine tumor", "Stage II", "Everolimus", "needs_review", "michael_net"),
            ("1042202", "Emma", "Wilson", date(1958, 11, 6), "F", "Pancreatic ductal adenocarcinoma", "Stage II", "Observation cohort", "watch", "adc_flat"),
            ("1042203", "James", "Rodriguez", date(1969, 1, 20), "M", "Pancreatic cancer", "Stage IV", "Gemcitabine monotherapy narrative", "watch", "adc_rising"),
            ("1042204", "Olivia", "Patel", date(1975, 7, 8), "F", "Pancreatic adenocarcinoma", "Stage IV", "Gemcitabine + nab-paclitaxel documented", "stable", "adc_rising"),
            ("1042205", "Robert", "Kim", date(1955, 3, 3), "M", "Pancreatic ductal adenocarcinoma", "Stage III", "FOLFIRINOX", "needs_review", "adc_rising"),
            ("1042206", "Maria", "Garcia", date(1967, 9, 15), "F", "Metastatic pancreatic ductal adenocarcinoma", "Stage IV", "Clinical trial evaluation narrative", "needs_review", "adc_rising"),
            ("1042207", "Alan", "Brooks", date(1980, 12, 1), "M", "Pancreatic head mass diagnostic work-up", "Pending definitive staging narrative", "Biopsy-planning regimen", "watch", "adc_flat"),
            ("1042208", "Nina", "Shah", date(1962, 4, 29), "F", "Pancreatic ductal adenocarcinoma status post pancreaticoduodenectomy narrative", "Adjuvant context", "Surveillance regimen", "stable", "adc_flat"),
            ("1042209", "David", "Miller", date(1950, 6, 18), "M", "Pancreatic adenocarcinoma", "Stage II", "Adjuvant chemotherapy narrative", "stable", "adc_flat"),
            ("1042210", "Grace", "Thompson", date(1978, 8, 7), "F", "Pancreatic cystic lesion surveillance", "Benign/low-grade narrative focus", "Serial imaging regimen", "watch", "light"),
            ("1042211", "Henry", "Walker", date(1948, 2, 25), "M", "Pancreatic adenocarcinoma", "Stage III", "Radiation evaluation narrative", "needs_review", "adc_rising"),
            ("1042212", "Lisa", "Nguyen", date(1968, 4, 12), "F", "Colorectal adenocarcinoma", "Stage III", "FOLFOX", "needs_review", "crc"),
            ("1042213", "Thomas", "Reed", date(1959, 9, 22), "M", "Colon cancer metastatic", "Stage IV", "Bevacizumab regimen narrative", "watch", "crc"),
            ("1042214", "Rachel", "Torres", date(1972, 1, 30), "F", "Lung adenocarcinoma", "Stage IV", "Pembrolizumab", "needs_review", "lung"),
            ("1042215", "Steven", "Park", date(1954, 7, 14), "M", "Non-small cell lung cancer", "Stage IIIB", "Osimertinib narrative", "watch", "lung"),
            ("1042216", "Amanda", "Foster", date(1963, 11, 9), "F", "Breast cancer invasive ductal", "Stage II", "Adjuvant therapy narrative", "stable", "breast"),
            ("1042217", "Julia", "Nass", date(1970, 6, 21), "F", "Breast cancer metastatic", "Stage IV", "Trastuzumab regimen", "needs_review", "breast"),
            ("1042218", "Kevin", "Doyle", date(1985, 3, 8), "M", "Classical Hodgkin lymphoma", "Stage II", "ABVD narrative", "stable", "general"),
            ("1042219", "Sandra", "Ellis", date(1951, 12, 3), "F", "Breast cancer metastatic", "Stage IV", "Palbociclib narrative", "watch", "breast"),
            ("1042220", "Denise", "Abrams", date(1966, 4, 2), "F", "Pancreatic neuroendocrine tumor", "Stage II", "Octreotide narrative", "watch", "michael_net"),
            ("1042221", "Ethan", "Price", date(1957, 8, 19), "M", "Pancreatic ductal adenocarcinoma", "Stage III", "FOLFIRINOX", "needs_review", "adc_rising"),
            ("1042222", "Yuki", "Tanaka", date(1973, 2, 11), "F", "Pancreatic adenocarcinoma", "Stage II", "Surveillance narrative", "stable", "adc_flat"),
            ("1042223", "Carlos", "Mendez", date(1961, 10, 30), "M", "Metastatic pancreatic ductal adenocarcinoma", "Stage IV", "Gemcitabine narrative", "watch", "adc_rising"),
            ("1042224", "Priya", "Singh", date(1979, 5, 25), "F", "Colorectal adenocarcinoma", "Stage III", "FOLFIRI narrative", "needs_review", "crc"),
            ("1042225", "Walter", "Cobb", date(1952, 1, 8), "M", "Colon cancer metastatic", "Stage IV", "Cetuximab narrative", "watch", "crc"),
            ("1042226", "Helen", "Brooks", date(1964, 7, 17), "F", "Lung adenocarcinoma", "Stage IV", "Chemo-immunotherapy narrative", "needs_review", "lung"),
            ("1042227", "Marcus", "Bell", date(1956, 12, 6), "M", "Non-small cell lung cancer", "Stage IIIA", "Concurrent chemoradiation narrative", "stable", "lung"),
            ("1042228", "Fiona", "Walsh", date(1971, 3, 22), "F", "Breast cancer invasive ductal", "Stage I", "Endocrine therapy narrative", "stable", "breast"),
            ("1042229", "Omar", "Hassan", date(1969, 9, 9), "M", "Breast cancer metastatic", "Stage IV", "CDK4/6 narrative", "watch", "breast"),
            ("1042230", "Linda", "Zhou", date(1958, 11, 28), "F", "Pancreatic cystic lesion surveillance", "Low-risk narrative", "MRI surveillance", "stable", "light"),
            ("1042231", "Quinn", "Reed", date(1988, 4, 4), "F", "Melanoma metastatic", "Stage IV", "Checkpoint inhibitor narrative", "needs_review", "general"),
            ("1042232", "Roger", "Ingram", date(1949, 6, 16), "M", "Pancreatic adenocarcinoma", "Stage IV", "Palliative care consult narrative", "watch", "adc_rising"),
            ("1042233", "Bethany", "Cole", date(1965, 1, 3), "F", "PDAC recurrent", "Stage IV", "Gemcitabine / nab-paclitaxel", "needs_review", "adc_flat"),
            ("1042234", "Ian", "Sullivan", date(1977, 8, 30), "M", "Pancreatic head mass diagnostic work-up", "Staging pending", "EUS planning narrative", "watch", "adc_flat"),
        ]

        cohort: list[Patient] = []
        for row in specs:
            mrn, first, last, dob, sex, dx, stage, rx, status, _kind = row
            cohort.append(
                Patient.objects.create(
                    medical_record_number=mrn,
                    first_name=first,
                    last_name=last,
                    date_of_birth=dob,
                    sex=sex,
                    primary_diagnosis=dx,
                    cancer_stage=stage,
                    current_treatment=rx,
                    review_status=status,
                )
            )

        for p in cohort:
            seed_condition_encounter(p, alex)

        kind_by_mrn = {row[0]: row[9] for row in specs}

        for p in cohort:
            kind = kind_by_mrn[p.medical_record_number]
            if kind == "sarah":
                seed_sarah_flagship(p, alex, nurse)
            elif kind == "michael_net":
                seed_michael_net(p, alex, nurse)
            elif kind == "adc_rising":
                seed_pancreatic_adc_rich(p, alex, nurse, rising_ca19=True)
            elif kind == "adc_flat":
                seed_pancreatic_adc_rich(p, alex, nurse, rising_ca19=False)
            elif kind == "crc":
                seed_crc_chart(p, alex, nurse)
            elif kind == "lung":
                seed_lung_chart(p, alex, nurse)
            elif kind == "breast":
                seed_breast_chart(p, alex, nurse)
            elif kind == "light":
                seed_light_chart(p, alex)
            elif kind == "general":
                seed_general_oncology_chart(p, alex, nurse)

        stable_demo = Patient.objects.get(medical_record_number="1042218")
        Observation.objects.filter(patient=stable_demo).delete()
        SourceBackedObservation.objects.filter(patient=stable_demo).delete()
        DiagnosticReport.objects.filter(patient=stable_demo).delete()
        r = DiagnosticReport.objects.create(
            patient=stable_demo,
            title="Stable regression lab",
            raw_text="Synthetic stable marker row narrative.",
            uploaded_by=alex,
        )
        for v, d in [(32, date(2025, 1, 1)), (35, date(2025, 2, 1))]:
            Observation.objects.create(
                patient=stable_demo,
                report=r,
                observation_type="tumor_marker",
                name="CA 19-9",
                value_number=v,
                observed_at=d,
                confirmation_status="confirmed",
                confirmed_by=alex,
            )
        generate_source_backed_observations(stable_demo)

        self.stdout.write(
            self.style.SUCCESS(
                f"Synthetic demo seeded ({len(DEMO_MRNS)} patients). Logins alex.morgan.demo / jamie.lee.demo / priya.shah.demo (password123)."
            )
        )
