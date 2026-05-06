from django.contrib import admin

from .models import EvidenceItem, Observation, SearchIndexEntry, SourceBackedObservation


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ("name", "patient", "observation_type", "confirmation_status", "observed_at")
    list_filter = ("observation_type", "confirmation_status")
    search_fields = ("name", "value_text", "patient__last_name")
    raw_id_fields = ("patient", "report")


@admin.register(EvidenceItem)
class EvidenceItemAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "source_type", "evidence_date")
    list_filter = ("source_type",)
    search_fields = ("title", "snippet", "patient__last_name")


@admin.register(SourceBackedObservation)
class SourceBackedObservationAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "status", "reviewed")
    list_filter = ("status", "reviewed")
    search_fields = ("title", "explanation", "patient__last_name")
    filter_horizontal = ("evidence_items",)


@admin.register(SearchIndexEntry)
class SearchIndexEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "source_type", "created_at")
    list_filter = ("source_type",)
