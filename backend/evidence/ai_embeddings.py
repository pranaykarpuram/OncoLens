"""
Local semantic retrieval for chart text already indexed in SearchIndexEntry.

This module uses sentence embeddings only to rank **existing** snippets—never to invent
diagnoses or treatment plans. Explainable, rules-based flags (`generate_source_backed_observations`
and parsers) remain primary; cosine similarity is an extra retrieval channel.

Model weights download on first use (~MB) to the Hugging Face cache (typically ~/.cache/huggingface).
Expect roughly hundreds of MB RAM while encoding. For production Postgres, pgvector could replace
JSON float lists; SQLite stores embeddings as JSON arrays only in this phase.

Workflow after loading demo data: ``python manage.py seed_demo_data`` then
``python manage.py rebuild_embeddings`` (optional ``--reindex-first`` if indices are stale).
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from evidence.models import SearchIndexEntry

logger = logging.getLogger(__name__)

_MODEL = None


def get_embedding_model():
    """Lazy singleton SentenceTransformer; override with ONCOLENS_EMBEDDING_MODEL."""
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer

        name = os.environ.get(
            "ONCOLENS_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
        _MODEL = SentenceTransformer(name)
    return _MODEL


def embed_text(text: str) -> List[float]:
    """Return a single embedding vector as a list of floats; empty input → empty list."""
    import numpy as np

    t = (text or "").strip()
    if not t:
        return []
    model = get_embedding_model()
    vec = model.encode([t], normalize_embeddings=True)[0]
    return np.asarray(vec, dtype=np.float64).tolist()


def embedding_vector_for_entry(entry: SearchIndexEntry) -> List[float]:
    """Embed the same blob used for lexical search (search_text, else title + body)."""
    blob = (entry.search_text or "").strip()
    if not blob:
        blob = f"{(entry.title or '').strip()}\n{(entry.text or '').strip()}".strip()
    return embed_text(blob)


def rebuild_all_search_embeddings(
    batch_size: int = 32,
    patient_id: Optional[int] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Batch-encode SearchIndexEntry rows missing embeddings (unless force).

    Returns counts: embedded, skipped, errors.
    """
    import numpy as np
    from django.db.models import Q

    stats = {"embedded": 0, "skipped": 0, "errors": 0}

    qs = SearchIndexEntry.objects.all().order_by("pk")
    if patient_id is not None:
        qs = qs.filter(patient_id=patient_id)
    if not force:
        qs = qs.filter(Q(embedding__isnull=True) | Q(embedding=[]))

    try:
        model = get_embedding_model()
    except Exception as exc:
        logger.warning("Could not load embedding model: %s", exc)
        stats["skipped"] = qs.count()
        stats["errors"] = stats["skipped"]
        return stats

    batch_ids: List[int] = []
    batch_texts: List[str] = []

    def flush():
        nonlocal batch_ids, batch_texts
        if not batch_ids:
            return
        try:
            vectors = model.encode(batch_texts, normalize_embeddings=True, batch_size=len(batch_ids))
            for pk, row in zip(batch_ids, vectors):
                vec = np.asarray(row, dtype=np.float64).tolist()
                SearchIndexEntry.objects.filter(pk=pk).update(embedding=vec)
                stats["embedded"] += 1
        except Exception as exc:
            logger.warning("Embedding batch failed: %s", exc)
            stats["errors"] += len(batch_ids)
        batch_ids = []
        batch_texts = []

    for entry in qs.iterator(chunk_size=256):
        blob = (entry.search_text or "").strip()
        if not blob:
            blob = f"{(entry.title or '').strip()}\n{(entry.text or '').strip()}".strip()
        if not blob:
            stats["skipped"] += 1
            continue
        batch_ids.append(entry.pk)
        batch_texts.append(blob)
        if len(batch_ids) >= batch_size:
            flush()
    flush()

    return stats


def semantic_search_candidates(
    query: str,
    patient_id: Optional[int] = None,
    top_k: int = 50,
) -> List[Tuple[SearchIndexEntry, float]]:
    """
    Rank indexed rows by cosine similarity to the query embedding.

    Requires non-empty query and rows with non-null, non-empty JSON embeddings.
    """
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    q = (query or "").strip()
    if not q:
        return []

    try:
        model = get_embedding_model()
        q_raw = model.encode([q], normalize_embeddings=True)[0]
        q_vec = np.asarray(q_raw, dtype=np.float64).reshape(1, -1)
    except Exception as exc:
        logger.warning("Semantic search skipped (model/query encode failed): %s", exc)
        return []

    qs = SearchIndexEntry.objects.select_related("patient").exclude(embedding__isnull=True)
    if patient_id is not None:
        qs = qs.filter(patient_id=patient_id)

    entries: List[SearchIndexEntry] = []
    for entry in qs.iterator(chunk_size=400):
        emb = entry.embedding
        if not isinstance(emb, list) or len(emb) == 0:
            continue
        entries.append(entry)
        if len(entries) >= 5000:
            break

    if not entries:
        return []

    mat = np.asarray([e.embedding for e in entries], dtype=np.float64)
    try:
        sims = cosine_similarity(q_vec, mat)[0]
    except Exception as exc:
        logger.warning("cosine_similarity failed: %s", exc)
        return []

    order = np.argsort(-sims)[:top_k]
    return [(entries[i], float(sims[i])) for i in order]

