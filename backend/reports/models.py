from django.conf import settings
from django.db import models


class DiagnosticReport(models.Model):
    REPORT_TYPES = [
        ("lab", "Lab Report"),
        ("pathology", "Pathology Report"),
        ("imaging", "Imaging Report"),
        ("oncology_note", "Oncology Note"),
        ("other", "Other"),
    ]
    PARSE_STATUS = [
        ("pending", "Pending"),
        ("parsed", "Parsed"),
        ("needs_confirmation", "Needs Confirmation"),
        ("failed", "Failed"),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="reports",
    )
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, default="other")
    title = models.CharField(max_length=255)
    report_date = models.DateField(null=True, blank=True)
    uploaded_file = models.FileField(upload_to="reports/", null=True, blank=True)
    raw_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    parse_status = models.CharField(
        max_length=50, choices=PARSE_STATUS, default="pending"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date", "-created_at"]

    def __str__(self):
        return f"{self.patient.full_name}: {self.title}"
