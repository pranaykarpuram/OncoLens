"""
Batch-compute SearchIndexEntry embeddings (sentence-transformers).

After seeding demo data, run: ``python manage.py rebuild_embeddings``.
Use ``--reindex-first`` to rebuild lexical chunks from chart rows first (clears old embeddings).

Model cache: ~/.cache/huggingface (or HF_HOME). Expect RAM usage while encoding.
"""

from django.core.management.base import BaseCommand

from evidence.ai_embeddings import rebuild_all_search_embeddings
from evidence.search_index import reindex_all, reindex_patient


class Command(BaseCommand):
    help = "Compute or refresh JSON embeddings on SearchIndexEntry (local sentence-transformers)."

    def add_arguments(self, parser):
        parser.add_argument("--patient-id", type=int, default=None, help="Limit to one patient.")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-embed all rows for the queryset (not only missing embeddings).",
        )
        parser.add_argument(
            "--reindex-first",
            action="store_true",
            help="Rebuild SearchIndexEntry lexical rows from DB before embedding.",
        )

    def handle(self, *args, **options):
        pid = options["patient_id"]
        if options["reindex_first"]:
            self.stdout.write("Reindexing lexical search rows…")
            if pid is not None:
                from patients.models import Patient

                reindex_patient(Patient.objects.get(pk=pid))
            else:
                reindex_all()
            self.stdout.write(self.style.SUCCESS("Reindex complete."))

        stats = rebuild_all_search_embeddings(
            patient_id=pid,
            force=options["force"],
        )
        self.stdout.write(
            f"Embedded: {stats['embedded']}, skipped: {stats['skipped']}, errors: {stats['errors']}"
        )
