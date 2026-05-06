from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse


class Patient(models.Model):
    STATUS_CHOICES = [
        ("stable", "Stable"),
        ("watch", "Watch"),
        ("needs_review", "Needs Review"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=20, blank=True)
    medical_record_number = models.CharField(max_length=50, unique=True)
    primary_diagnosis = models.CharField(max_length=255)
    cancer_stage = models.CharField(max_length=50, blank=True)
    current_treatment = models.CharField(max_length=255, blank=True)
    review_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="stable")
    last_chart_review_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When a clinician last marked this chart reviewed in OncoLens.",
    )
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        today = date.today()
        dob = self.date_of_birth
        years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return years

    @property
    def initials(self):
        fn = (self.first_name or "")[:1]
        ln = (self.last_name or "")[:1]
        return f"{fn}{ln}".upper()

    def get_absolute_url(self):
        return reverse("patients:workspace", kwargs={"pk": self.pk})


class Condition(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="conditions"
    )
    name = models.CharField(max_length=255)
    stage = models.CharField(max_length=100, blank=True)
    diagnosis_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name}: {self.name}"


class Encounter(models.Model):
    ENCOUNTER_TYPES = [
        ("clinic_visit", "Clinic Visit"),
        ("lab", "Lab"),
        ("imaging", "Imaging"),
        ("pathology", "Pathology"),
        ("treatment", "Treatment"),
        ("other", "Other"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="encounters"
    )
    encounter_type = models.CharField(max_length=50, choices=ENCOUNTER_TYPES)
    date = models.DateField()
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.patient} — {self.get_encounter_type_display()} ({self.date})"


class Treatment(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="treatments"
    )
    name = models.CharField(max_length=255)
    treatment_type = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "-pk"]

    def __str__(self):
        return f"{self.patient.full_name}: {self.name}"


class ClinicalNote(models.Model):
    NOTE_TYPES = [
        ("visit", "Visit Note"),
        ("nursing", "Nursing Note"),
        ("tumor_board", "Tumor Board Note"),
        ("follow_up", "Follow-up Note"),
        ("other", "Other"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="clinical_notes"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    note_type = models.CharField(max_length=50, choices=NOTE_TYPES, default="visit")
    text = models.TextField()
    note_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-note_date", "-pk"]

    def __str__(self):
        return f"{self.patient.full_name} — {self.note_date}"
