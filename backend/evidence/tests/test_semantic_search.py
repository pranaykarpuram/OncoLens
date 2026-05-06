"""Semantic search and embedding paths (mocked; no Hugging Face download)."""

from __future__ import annotations

import math
from datetime import date
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from evidence.ai_embeddings import rebuild_all_search_embeddings
from evidence.models import SearchIndexEntry
from evidence.search import search_evidence
from patients.models import Patient


class RebuildEmbeddingsTests(TestCase):
    def test_rebuild_persists_embedding_json(self):
        User = get_user_model()
        User.objects.create_user(username="embusr", password="x")
        p = Patient.objects.create(
            medical_record_number="EMB1",
            first_name="Emb",
            last_name="Patient",
            date_of_birth=date(1960, 1, 1),
            primary_diagnosis="Demo",
            review_status="stable",
        )
        SearchIndexEntry.objects.create(
            patient=p,
            source_type="report",
            source_id=42,
            title="Labs",
            text="CA 19-9 rising on follow-up imaging.",
            search_text="ca 19-9 rising on follow-up imaging.",
            metadata={"chunk_index": 0, "source_date": "2026-01-01"},
        )

        class _FakeModel:
            def encode(self, texts, normalize_embeddings=True, batch_size=None):
                row = [0.25, 0.25, 0.25, 0.93541435]
                return [list(row) for _ in texts]

        with mock.patch("evidence.ai_embeddings.get_embedding_model", return_value=_FakeModel()):
            stats = rebuild_all_search_embeddings(batch_size=8, patient_id=p.pk)

        self.assertGreaterEqual(stats["embedded"], 1)
        entry = SearchIndexEntry.objects.get(patient=p)
        self.assertIsInstance(entry.embedding, list)
        self.assertEqual(len(entry.embedding), 4)


class SemanticFusionTests(TestCase):
    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.user = User.objects.create_user(username="semusr", password="x")
        self.p = Patient.objects.create(
            medical_record_number="SEM1",
            first_name="Sem",
            last_name="Patient",
            date_of_birth=date(1958, 3, 3),
            primary_diagnosis="Pancreatic adenocarcinoma",
            review_status="stable",
        )

    def test_semantic_ranking_prefers_higher_similarity(self):
        low = SearchIndexEntry.objects.create(
            patient=self.p,
            source_type="report",
            source_id=1,
            title="A",
            text="off topic narrative about billing codes",
            search_text="billing codes unrelated",
            metadata={"chunk_index": 0},
            embedding=[1.0, 0.0, 0.0],
        )
        high = SearchIndexEntry.objects.create(
            patient=self.p,
            source_type="report",
            source_id=2,
            title="B",
            text="CA19-9 tumor marker rising sharply per oncology note",
            search_text="ca19-9 tumor marker rising sharply per oncology note",
            metadata={"chunk_index": 0},
            embedding=[0.97, 0.24, 0.0],
        )

        def _cos(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(y * y for y in b))
            return (dot / (na * nb)) if na and nb else 0.0

        def fake_sem(q, patient_id=None, top_k=50):
            qv = [0.96, 0.28, 0.0]
            entries = [low, high]
            sims = [_cos(qv, list(e.embedding)) for e in entries]
            ranked = sorted(range(len(entries)), key=lambda i: sims[i], reverse=True)[:top_k]
            return [(entries[i], float(sims[i])) for i in ranked]

        with mock.patch("evidence.ai_embeddings.semantic_search_candidates", side_effect=fake_sem):
            hits = search_evidence("tumor marker getting worse", {"patient": self.p.pk, "top_k": 25})

        semantic_hits = [h for h in hits if h.get("result_kind") in ("semantic", "hybrid")]
        self.assertTrue(semantic_hits)
        top = semantic_hits[0]
        self.assertIn("CA19", top["matched_snippet"].upper().replace("-", ""))

    def test_keyword_only_when_semantic_returns_empty(self):
        SearchIndexEntry.objects.create(
            patient=self.p,
            source_type="clinical_note",
            source_id=9,
            title="Note · 2026-05-01",
            text="Gemcitabine regimen discussed.",
            search_text="gemcitabine regimen discussed.",
            metadata={"chunk_index": 0},
            embedding=None,
        )
        with mock.patch("evidence.ai_embeddings.semantic_search_candidates", return_value=[]):
            hits = search_evidence("Gemcitabine", {"patient": self.p.pk})
        self.assertTrue(any(h["patient"].pk == self.p.pk for h in hits))
        self.assertTrue(all(h.get("similarity_score") is None for h in hits))

    def test_semantic_branch_passes_patient_scope(self):
        with mock.patch("evidence.ai_embeddings.semantic_search_candidates", return_value=[]) as m:
            search_evidence("anything", {"patient": self.p.pk, "top_k": 10})
        m.assert_called_once()
        args, kwargs = m.call_args
        self.assertEqual(kwargs.get("patient_id"), self.p.pk)
        self.assertIn("top_k", kwargs)

    def test_semantic_disabled_on_import_error_resilience(self):
        def boom(*a, **kw):
            raise RuntimeError("simulated failure")

        SearchIndexEntry.objects.create(
            patient=self.p,
            source_type="clinical_note",
            source_id=11,
            title="N",
            text="Gemcitabine mentioned here too",
            search_text="gemcitabine mentioned here too",
            metadata={"chunk_index": 0},
        )
        with mock.patch("evidence.ai_embeddings.semantic_search_candidates", side_effect=boom):
            hits = search_evidence("Gemcitabine", {"patient": self.p.pk})
        self.assertTrue(any(h["patient"].pk == self.p.pk for h in hits))


class EvidenceSearchApiFieldsTests(TestCase):
    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.user = User.objects.create_user(username="apiemb", password="pass12345")
        self.client = Client()
        self.assertTrue(self.client.login(username="apiemb", password="pass12345"))
        self.p = Patient.objects.create(
            medical_record_number="APIE1",
            first_name="Api",
            last_name="Evidence",
            date_of_birth=date(1951, 1, 1),
            primary_diagnosis="Pancreatic adenocarcinoma",
            review_status="stable",
        )
        self._sem_patcher = mock.patch(
            "evidence.ai_embeddings.semantic_search_candidates",
            return_value=[],
        )
        self._sem_patcher.start()

    def tearDown(self):
        self._sem_patcher.stop()
        super().tearDown()

    def test_api_includes_new_fields_and_suggested_terms(self):
        SearchIndexEntry.objects.create(
            patient=self.p,
            source_type="report",
            source_id=55,
            title="Chart",
            text="UniqueApiTokenZZ gemcitabine plan",
            search_text="uniqueapitokenzz gemcitabine plan",
            metadata={"chunk_index": 0, "source_date": "2026-04-01"},
        )
        r = self.client.get(
            "/api/evidence/search/",
            {"q": "UniqueApiTokenZZ", "patient": str(self.p.pk), "top_k": "5"},
        )
        self.assertEqual(r.status_code, 200)
        payload = r.json()
        self.assertIn("suggested_terms", payload)
        self.assertGreater(len(payload["suggested_terms"]), 0)
        row = payload["results"][0]
        self.assertIn("result_kind", row)
        self.assertIn("similarity_score", row)
        self.assertIn("source_date", row)
        self.assertIn("chunk_index", row)
        self.assertIn("source_id", row)
