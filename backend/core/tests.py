"""Tests for chart review windows, mark-reviewed API, and queue cohort rules."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone as dj_tz

from core.chart_review import patient_in_review_queue
from evidence.models import EvidenceItem, Observation, SourceBackedObservation
from evidence.workspace_insights import build_what_changed_window
from patients.models import Patient
from reports.models import DiagnosticReport


class ChartReviewWindowTests(TestCase):
    def test_rolling_fallback_without_last_review(self):
        p = Patient.objects.create(
            medical_record_number="CRROLL",
            first_name="Roll",
            last_name="Back",
            date_of_birth=date(1960, 1, 1),
            primary_diagnosis="Demo dx",
            review_status="stable",
        )
        ref = date(2026, 6, 1)
        w = build_what_changed_window(p, reference_date=ref)
        self.assertEqual(w["mode"], "rolling")
        self.assertEqual(w["cutoff_date"], ref - timedelta(days=56))
        self.assertIn("recently", w["label"].lower())

    def test_since_review_when_last_review_set(self):
        p = Patient.objects.create(
            medical_record_number="CRSINCE",
            first_name="Since",
            last_name="Review",
            date_of_birth=date(1960, 1, 1),
            primary_diagnosis="Demo dx",
            review_status="stable",
            last_chart_review_at=dj_tz.make_aware(datetime(2026, 4, 12, 15, 30, 0)),
        )
        ref = date(2026, 5, 15)
        w = build_what_changed_window(p, reference_date=ref)
        self.assertEqual(w["mode"], "since_review")
        self.assertEqual(w["cutoff_date"], date(2026, 4, 12))


class MarkReviewedApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="mru", password="pw987654!")
        self.client = Client()
        self.assertTrue(self.client.login(username="mru", password="pw987654!"))
        self.p = Patient.objects.create(
            medical_record_number="MRAPI1",
            first_name="Mark",
            last_name="Api",
            date_of_birth=date(1955, 1, 1),
            primary_diagnosis="Demo",
            review_status="needs_review",
        )
        rep = DiagnosticReport.objects.create(patient=self.p, title="R", raw_text="x", uploaded_by=self.user)
        self.so = SourceBackedObservation.objects.create(
            patient=self.p,
            title="Flag demo",
            explanation="Excerpt",
            status="watch",
            reason="__rule__:test",
            reviewed=False,
        )
        self.ei = EvidenceItem.objects.create(
            patient=self.p,
            source_type="report",
            source_id=rep.pk,
            title="Rep",
            snippet="snip",
            evidence_date=date(2026, 1, 1),
            reviewed=False,
        )
        self.so.evidence_items.add(self.ei)

    def test_mark_reviewed_sets_timestamp_and_reviewed_flags(self):
        before = self.p.last_chart_review_at
        self.assertIsNone(before)

        resp = self.client.post(f"/api/patients/{self.p.pk}/mark-reviewed/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertIsNotNone(data["patient"]["last_chart_review_at"])

        self.p.refresh_from_db()
        self.assertIsNotNone(self.p.last_chart_review_at)

        self.so.refresh_from_db()
        self.assertTrue(self.so.reviewed)
        self.ei.refresh_from_db()
        self.assertTrue(self.ei.reviewed)


class ReviewQueueCohortTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="rqcoh", password="pw987654!")
        self.client = Client()
        self.assertTrue(self.client.login(username="rqcoh", password="pw987654!"))

    def test_queue_excludes_clean_stable_chart_after_review(self):
        """Stable patient fully reviewed without new ingestion should drop off queue."""

        p = Patient.objects.create(
            medical_record_number="RQCLEAN",
            first_name="Clean",
            last_name="Queue",
            date_of_birth=date(1960, 5, 5),
            primary_diagnosis="Demo",
            review_status="stable",
            last_chart_review_at=dj_tz.now() - timedelta(days=3),
        )
        r = DiagnosticReport.objects.create(
            patient=p,
            title="Old report",
            raw_text="Synthetic",
            uploaded_by=self.user,
            parse_status="parsed",
        )
        # Ingestion timestamp defaults to now; bump it before last review so it is not "new since review"
        DiagnosticReport.objects.filter(pk=r.pk).update(created_at=dj_tz.now() - timedelta(days=30))
        # No unreviewed flags, pipeline clean, observations none
        self.assertFalse(patient_in_review_queue(p))

    def test_queue_includes_unreviewed_source_flag(self):
        p = Patient.objects.create(
            medical_record_number="RQFLAG",
            first_name="Flag",
            last_name="Queue",
            date_of_birth=date(1960, 5, 5),
            primary_diagnosis="Demo",
            review_status="stable",
            last_chart_review_at=dj_tz.now(),
        )
        SourceBackedObservation.objects.create(
            patient=p,
            title="Open flag",
            explanation="x",
            status="needs_review",
            reason="__rule__:t",
            reviewed=False,
        )
        self.assertTrue(patient_in_review_queue(p))

    def test_review_queue_endpoint_returns_ordered_cohort_json(self):
        p1 = Patient.objects.create(
            medical_record_number="RQEP1",
            first_name="A",
            last_name="Needs",
            date_of_birth=date(1960, 1, 1),
            primary_diagnosis="Demo",
            review_status="needs_review",
        )
        Observation.objects.create(
            patient=p1,
            observation_type="lab",
            name="Loose",
            value_text="?",
            confirmation_status="unconfirmed",
            confidence=0.5,
            observed_at=date(2026, 1, 10),
            confirmed_by=None,
        )
        resp = self.client.get("/api/review-queue/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        ids = [row["id"] for row in data["patients"]]
        self.assertIn(p1.pk, ids)
        self.assertIn("patients_pending_chart_review", data["metrics"])
