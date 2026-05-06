from django.conf import settings
from django.db import models


class TumorBoardBrief(models.Model):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="tumor_board_briefs",
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    case_summary = models.TextField(blank=True)
    treatment_course = models.TextField(blank=True)
    key_timeline_events = models.JSONField(default=list, blank=True)
    evidence_of_change = models.JSONField(default=list, blank=True)
    missing_or_unconfirmed_data = models.JSONField(default=list, blank=True)
    source_documents = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Brief for {self.patient.full_name} ({self.created_at.date()})"
