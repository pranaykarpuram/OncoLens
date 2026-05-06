from django.contrib import admin

from .models import ClinicalNote, Condition, Encounter, Patient, Treatment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "medical_record_number", "review_status", "primary_diagnosis")
    list_filter = ("review_status", "primary_diagnosis")
    search_fields = ("first_name", "last_name", "medical_record_number")


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 0


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("name", "patient", "stage", "diagnosis_date", "status")
    list_filter = ("status",)
    search_fields = ("name", "patient__last_name")


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ("patient", "encounter_type", "date", "provider")
    list_filter = ("encounter_type",)
    search_fields = ("patient__last_name", "summary")


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "name", "treatment_type", "start_date", "status")
    search_fields = ("name", "patient__last_name")


@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ("patient", "note_type", "note_date", "author")
    list_filter = ("note_type",)
    search_fields = ("text", "patient__last_name")
