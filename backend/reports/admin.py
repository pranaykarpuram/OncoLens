from django.contrib import admin

from .models import DiagnosticReport


@admin.register(DiagnosticReport)
class DiagnosticReportAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "report_type", "parse_status", "report_date", "uploaded_by")
    list_filter = ("report_type", "parse_status")
    search_fields = ("title", "raw_text", "patient__last_name", "patient__medical_record_number")
    raw_id_fields = ("patient",)
