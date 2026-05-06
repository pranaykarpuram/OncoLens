from datetime import date
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.seed_demo import seed_michael_net, seed_sarah_flagship
from evidence.models import Observation, SourceBackedObservation
from evidence.workspace_insights import build_what_changed_summary
from evidence.services import generate_source_backed_observations
from evidence.search import search_evidence
from patients.models import Patient
from reports.models import DiagnosticReport
from reports.parsers import parse_report_text
from reports.services import apply_parse_to_report


class ParserTests(TestCase):
    def test_ca19_extracts_from_text(self):
        rep = SimpleNamespace(
            raw_text="CA 19-9 measured at 780 U/mL",
            report_type="lab",
            report_date=None,
        )
        out = parse_report_text(rep)
        self.assertGreaterEqual(len(out.get("labs", [])), 1)
        lab = out["labs"][0]
        self.assertIn("CA", lab.get("name", ""))
        self.assertEqual(lab.get("value_number"), 780.0)

    def test_chromogranin_extracts_from_text(self):
        rep = SimpleNamespace(
            raw_text="Chromogranin A measured at 410 ng/mL, elevated.",
            report_type="lab",
            report_date=None,
        )
        out = parse_report_text(rep)
        labs = out.get("labs", [])
        cg = [x for x in labs if "Chromogranin" in (x.get("name") or "")]
        self.assertTrue(cg)
        self.assertEqual(cg[0].get("value_number"), 410.0)

    def test_cea_and_ca153_extract(self):
        rep = SimpleNamespace(
            raw_text="CEA is 14.6 ng/mL. CA 15-3 measured at 56 U/mL.",
            report_type="lab",
            report_date=None,
        )
        out = parse_report_text(rep)
        names = [x.get("name") for x in out.get("labs", [])]
        self.assertTrue(any("CEA" == n for n in names))
        self.assertTrue(any("CA 15-3" in (n or "") for n in names))

    def test_junk_text_returns_empty_buckets(self):
        rep = SimpleNamespace(raw_text="nothing clinical here ***", report_type="other", report_date=None)
        out = parse_report_text(rep)
        self.assertEqual(len(out.get("labs", [])), 0)


class SourceBackedRulesTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tuser", password="x")
        self.p = Patient.objects.create(
            medical_record_number="TST0001",
            first_name="Trend",
            last_name="Patient",
            date_of_birth=date(1960, 1, 1),
            primary_diagnosis="Test",
            cancer_stage="III",
            current_treatment="Chemo narrative",
            review_status="stable",
        )
        r = DiagnosticReport.objects.create(
            patient=self.p,
            title="Lab",
            raw_text="Synthetic",
            uploaded_by=self.user,
        )
        for v, d in [(10, date(2025, 1, 1)), (20, date(2025, 2, 1)), (30, date(2025, 3, 1))]:
            Observation.objects.create(
                patient=self.p,
                report=r,
                observation_type="tumor_marker",
                name="CA 19-9",
                value_number=v,
                observed_at=d,
                confirmation_status="confirmed",
                confirmed_by=self.user,
            )

    def test_ca19_trend_rule_creates_flag(self):
        created = generate_source_backed_observations(self.p)
        titles = [o.title for o in created]
        self.assertTrue(any("CA 19-9" in t for t in titles))
        self.assertTrue(
            SourceBackedObservation.objects.filter(patient=self.p, title__icontains="CA 19-9").exists()
        )


class NetTrendRuleTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="netuser", password="x")
        self.p = Patient.objects.create(
            medical_record_number="NET999",
            first_name="Net",
            last_name="Trend",
            date_of_birth=date(1965, 6, 1),
            primary_diagnosis="Pancreatic neuroendocrine tumor",
            cancer_stage="II",
            current_treatment="Everolimus narrative",
            review_status="stable",
        )
        r = DiagnosticReport.objects.create(patient=self.p, title="Labs", raw_text="x", uploaded_by=self.user)
        for v, d in [(220.0, date(2026, 1, 20)), (260.0, date(2026, 2, 15)), (410.0, date(2026, 3, 12))]:
            Observation.objects.create(
                patient=self.p,
                report=r,
                observation_type="tumor_marker",
                name="Chromogranin A",
                value_number=v,
                observed_at=d,
                confirmation_status="confirmed",
                confirmed_by=self.user,
            )

    def test_chromogranin_trend_rule(self):
        generate_source_backed_observations(self.p)
        self.assertTrue(
            SourceBackedObservation.objects.filter(
                patient=self.p, title__icontains="Chromogranin"
            ).exists()
        )


class StablePatientTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tuser2", password="x")
        self.p = Patient.objects.create(
            medical_record_number="TST0002",
            first_name="Flat",
            last_name="Labs",
            date_of_birth=date(1960, 1, 1),
            primary_diagnosis="Test",
            review_status="stable",
        )
        r = DiagnosticReport.objects.create(patient=self.p, title="L", raw_text="x", uploaded_by=self.user)
        for v, d in [(32, date(2025, 1, 1)), (35, date(2025, 2, 1))]:
            Observation.objects.create(
                patient=self.p,
                report=r,
                observation_type="tumor_marker",
                name="CA 19-9",
                value_number=v,
                observed_at=d,
                confirmation_status="confirmed",
                confirmed_by=self.user,
            )

    def test_stable_pair_no_consecutive_increase_rule(self):
        generate_source_backed_observations(self.p)
        self.assertFalse(
            SourceBackedObservation.objects.filter(
                patient=self.p, title__icontains="CA 19-9 has increased"
            ).exists()
        )


class SearchApiTests(TestCase):
    def setUp(self):
        super().setUp()
        self._sem_patcher = mock.patch(
            "evidence.ai_embeddings.semantic_search_candidates",
            return_value=[],
        )
        self._sem_patcher.start()

    def tearDown(self):
        self._sem_patcher.stop()
        super().tearDown()

    def test_search_includes_source_backed_observation_hits(self):
        User = get_user_model()
        u = User.objects.create_user(username="sofind", password="x")
        p = Patient.objects.create(
            medical_record_number="SO1",
            first_name="Src",
            last_name="Obs",
            date_of_birth=date(1955, 5, 5),
            primary_diagnosis="Pancreatic adenocarcinoma",
            review_status="stable",
        )
        SourceBackedObservation.objects.create(
            patient=p,
            title="UniqueMarkerPhrase XYZ123ZZ",
            explanation="Demonstration explanation block for search.",
            status="info",
            reason="__rule__:demo",
        )
        hits = search_evidence("XYZ123ZZ", {})
        self.assertTrue(any(h["patient"].pk == p.pk for h in hits))

    def test_search_returns_when_indexed(self):
        User = get_user_model()
        u = User.objects.create_user(username="su", password="x")
        p = Patient.objects.create(
            medical_record_number="SRCH1",
            first_name="Sam",
            last_name="Seek",
            date_of_birth=date(1955, 5, 5),
            primary_diagnosis="Demo",
            review_status="stable",
        )
        DiagnosticReport.objects.create(
            patient=p,
            title="Note",
            raw_text="Gemcitabine mentioned in synthetic documentation",
            uploaded_by=u,
        )
        hits = search_evidence("Gemcitabine", {})
        self.assertTrue(any(h["patient"].pk == p.pk for h in hits))


class ExtractPipelineTests(TestCase):
    def test_apply_parse_creates_unconfirmed_rows(self):
        User = get_user_model()
        u = User.objects.create_user(username="eu", password="x")
        p = Patient.objects.create(
            medical_record_number="EXT1",
            first_name="Extra",
            last_name="Ctor",
            date_of_birth=date(1950, 1, 1),
            primary_diagnosis="Demo",
            review_status="stable",
        )
        r = DiagnosticReport.objects.create(
            patient=p,
            title="Lab ingest",
            raw_text="Total bilirubin 1.8 mg/dL\nCA 19-9 is 400 U/mL",
            uploaded_by=u,
        )
        apply_parse_to_report(r)
        self.assertGreater(Observation.objects.filter(report=r).count(), 0)


class JsonApiSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="apiu", password="pass12345")
        self.client = Client()
        self.assertTrue(self.client.login(username="apiu", password="pass12345"))
        self.p = Patient.objects.create(
            medical_record_number="API1",
            first_name="Api",
            last_name="Patient",
            date_of_birth=date(1950, 1, 1),
            primary_diagnosis="Dx",
            review_status="stable",
        )

    def test_queue_and_evidence_endpoints(self):
        r1 = self.client.get("/api/review-queue/")
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.get(f"/api/patients/{self.p.pk}/evidence/")
        self.assertEqual(r2.status_code, 200)
        data = r2.json()
        self.assertIsInstance(data.get("what_changed_summary"), list)
        self.assertIn("summary_text", data.get("evidence_summary") or {})
        self.assertIn("source_count", data.get("evidence_summary") or {})
        w = data.get("what_changed_window") or {}
        self.assertEqual(w.get("mode"), "rolling")
        self.assertIn("start", w)
        self.assertIn("end", w)


class WorkspaceInsightsFlagshipTests(TestCase):
    """Seeded flagship charts — fixed reference anchor so windowing is deterministic."""

    def setUp(self):
        User = get_user_model()
        self.alex = User.objects.create_user(username="iwalex", password="pw999999!")
        self.nurse = User.objects.create_user(username="iwnurse", password="pw999999!")
        self.sarah = Patient.objects.create(
            medical_record_number="IW-SARAH",
            first_name="Sarah",
            last_name="Johnson",
            date_of_birth=date(1964, 2, 14),
            sex="F",
            primary_diagnosis="Pancreatic adenocarcinoma",
            cancer_stage="Stage III",
            current_treatment="FOLFIRINOX narrative",
            review_status="needs_review",
        )
        seed_sarah_flagship(self.sarah, self.alex, self.nurse)
        self.michael = Patient.objects.create(
            medical_record_number="IW-MIKE",
            first_name="Michael",
            last_name="Chen",
            date_of_birth=date(1971, 5, 2),
            sex="M",
            primary_diagnosis="Pancreatic neuroendocrine tumor",
            cancer_stage="Stage II",
            current_treatment="Everolimus narrative",
            review_status="needs_review",
        )
        seed_michael_net(self.michael, self.alex, self.nurse)

    def test_sarah_bullets_profile_terms(self):
        ref = date(2026, 5, 1)
        bullets = build_what_changed_summary(self.sarah, reference_date=ref)
        self.assertGreaterEqual(len(bullets), 3)
        joined = " ".join(b["text"] for b in bullets).lower()
        self.assertIn("ca 19-9", joined)
        self.assertTrue(any("imaging" in b["text"].lower() for b in bullets))
        self.assertTrue(
            any(("fatigue" in b["text"].lower() or "weight" in b["text"].lower()) for b in bullets),
        )
        self.assertTrue(any("bilirubin" in b["text"].lower() for b in bullets))

    def test_michael_bullets_profile_terms(self):
        ref = date(2026, 5, 1)
        bullets = build_what_changed_summary(self.michael, reference_date=ref)
        self.assertGreaterEqual(len(bullets), 3)
        joined = " ".join(b["text"] for b in bullets).lower()
        self.assertIn("chromogranin", joined)
        self.assertTrue(any("men1" in b["text"].lower() or "ki-67" in b["text"].lower() for b in bullets))
        self.assertTrue(any("mri" in b["text"].lower() for b in bullets))

    def test_stable_demo_light_language(self):
        User = get_user_model()
        p = Patient.objects.create(
            medical_record_number="IW-STABLE",
            first_name="Calm",
            last_name="Chart",
            date_of_birth=date(1985, 3, 8),
            sex="M",
            primary_diagnosis="Classical Hodgkin lymphoma narrative",
            review_status="stable",
        )
        r = DiagnosticReport.objects.create(patient=p, title="Labs", raw_text="x", uploaded_by=self.alex)
        for v, d in [(32, date(2025, 1, 1)), (35, date(2025, 2, 1))]:
            Observation.objects.create(
                patient=p,
                report=r,
                observation_type="tumor_marker",
                name="CA 19-9",
                value_number=v,
                observed_at=d,
                confirmation_status="confirmed",
                confirmed_by=self.alex,
            )
        bullets = build_what_changed_summary(p, reference_date=date(2025, 3, 15))
        joined = " ".join(b["text"] for b in bullets).lower()
        alarming = ("disease is progressing", "urgent escalation", "recommend initiation of")
        self.assertFalse(any(phrase in joined for phrase in alarming))
