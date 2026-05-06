from django.contrib import admin

from .models import TumorBoardBrief


@admin.register(TumorBoardBrief)
class TumorBoardBriefAdmin(admin.ModelAdmin):
    list_display = ("patient", "generated_by", "created_at")
    search_fields = ("patient__last_name", "case_summary")
    raw_id_fields = ("patient",)
