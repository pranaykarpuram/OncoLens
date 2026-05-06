from django.conf import settings
from django.db import models


class Observation(models.Model):
    OBSERVATION_TYPES = [
        ("tumor_marker", "Tumor Marker"),
        ("lab", "Lab"),
        ("vital", "Vital"),
        ("biomarker", "Biomarker"),
        ("symptom", "Symptom"),
        ("imaging_language", "Imaging Language"),
        ("other", "Other"),
    ]
    CONFIRMATION_STATUS = [
        ("unconfirmed", "Unconfirmed"),
        ("confirmed", "Confirmed"),
        ("rejected", "Rejected"),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="observations",
    )
    report = models.ForeignKey(
        "reports.DiagnosticReport",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="observations",
    )
    encounter = models.ForeignKey(
        "patients.Encounter",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="observations",
    )
    observation_type = models.CharField(max_length=50, choices=OBSERVATION_TYPES)
    name = models.CharField(max_length=255)
    value_text = models.CharField(max_length=255, blank=True)
    value_number = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    observed_at = models.DateField(null=True, blank=True)
    source_snippet = models.TextField(blank=True)
    confidence = models.FloatField(default=1.0)
    confirmation_status = models.CharField(
        max_length=30, choices=CONFIRMATION_STATUS, default="unconfirmed"
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-observed_at", "-pk"]

    def __str__(self):
        return f"{self.patient.full_name}: {self.name}"


class EvidenceItem(models.Model):
    SOURCE_TYPES = [
        ("report", "Report"),
        ("observation", "Observation"),
        ("note", "Clinical Note"),
        ("treatment", "Treatment"),
        ("timeline", "Timeline Event"),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="evidence_items",
    )
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    source_id = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=255)
    snippet = models.TextField()
    evidence_date = models.DateField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    confidence = models.FloatField(default=1.0)
    reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-evidence_date", "-pk"]

    def __str__(self):
        return self.title


class SourceBackedObservation(models.Model):
    STATUS_CHOICES = [
        ("info", "Info"),
        ("watch", "Watch"),
        ("needs_review", "Needs Review"),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="source_observations",
    )
    title = models.CharField(max_length=255)
    explanation = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="info")
    reason = models.TextField(blank=True)
    evidence_items = models.ManyToManyField(
        EvidenceItem,
        blank=True,
        related_name="source_observations",
    )
    evidence_json = models.JSONField(default=dict, blank=True)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class SearchIndexEntry(models.Model):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="search_entries",
    )
    source_type = models.CharField(max_length=50)
    source_id = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    search_text = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source_type}: {self.title}"
