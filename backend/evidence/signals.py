from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from evidence.models import EvidenceItem, Observation, SourceBackedObservation
from evidence.search_index import index_evidence_item, index_observation, index_source_backed_observation
from patients.models import ClinicalNote
from reports.models import DiagnosticReport


@receiver(post_save, sender=DiagnosticReport)
def update_report_search(sender, instance, **kwargs):
    from evidence.search_index import index_report

    index_report(instance)


@receiver(post_delete, sender=DiagnosticReport)
def remove_report_search(sender, instance, **kwargs):
    from evidence.models import SearchIndexEntry

    SearchIndexEntry.objects.filter(source_type="report", source_id=instance.pk).delete()


@receiver(post_save, sender=ClinicalNote)
def update_note_search(sender, instance, **kwargs):
    from evidence.search_index import index_clinical_note

    index_clinical_note(instance)


@receiver(post_delete, sender=ClinicalNote)
def remove_note_search(sender, instance, **kwargs):
    from evidence.models import SearchIndexEntry

    SearchIndexEntry.objects.filter(source_type="clinical_note", source_id=instance.pk).delete()


@receiver(post_save, sender=Observation)
def update_observation_search(sender, instance, **kwargs):
    index_observation(instance)


@receiver(post_delete, sender=Observation)
def remove_observation_search(sender, instance, **kwargs):
    from evidence.models import SearchIndexEntry

    SearchIndexEntry.objects.filter(source_type="observation", source_id=instance.pk).delete()


@receiver(post_save, sender=EvidenceItem)
def update_evidence_item_search(sender, instance, **kwargs):
    index_evidence_item(instance)


@receiver(post_delete, sender=EvidenceItem)
def remove_evidence_item_search(sender, instance, **kwargs):
    from evidence.models import SearchIndexEntry

    SearchIndexEntry.objects.filter(source_type="evidence_item", source_id=instance.pk).delete()


@receiver(post_save, sender=SourceBackedObservation)
def update_source_observation_search(sender, instance, **kwargs):
    index_source_backed_observation(instance)


@receiver(post_delete, sender=SourceBackedObservation)
def remove_source_observation_search(sender, instance, **kwargs):
    from evidence.models import SearchIndexEntry

    SearchIndexEntry.objects.filter(source_type="source_observation", source_id=instance.pk).delete()
