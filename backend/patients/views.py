from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from evidence.models import Observation, SourceBackedObservation
from patients.forms import ClinicalNoteForm, PatientSearchForm
from patients.models import Patient
from core.timeline import timeline_for_patient


@login_required
def patient_list(request):
    form = PatientSearchForm(request.GET)
    patients = Patient.objects.all()
    if form.is_valid() and form.cleaned_data.get("q"):
        term = form.cleaned_data["q"].strip()
        patients = patients.filter(
            Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
            | Q(medical_record_number__icontains=term)
            | Q(primary_diagnosis__icontains=term)
        )
    patients = patients.order_by("last_name", "first_name")
    return render(
        request,
        "patients/patient_list.html",
        {"patients": patients, "search_form": form},
    )


@login_required
def workspace(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == "POST" and request.POST.get("add_note"):
        note_form = ClinicalNoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.author = request.user
            note.patient = patient
            note.save()
            messages.success(request, "Clinical note saved for clinician review.")
            return redirect("patients:workspace", pk=patient.pk)
    else:
        note_form = ClinicalNoteForm(initial={"patient": patient})

    obs_grouped = {}
    observations = (
        Observation.objects.filter(patient=patient).select_related("report").order_by("-observed_at", "-pk")
    )
    for o in observations:
        obs_grouped.setdefault(o.observation_type, []).append(o)

    source_obs = (
        SourceBackedObservation.objects.filter(patient=patient).prefetch_related("evidence_items").order_by("-created_at")
    )

    ctx = {
        "patient": patient,
        "observations": observations,
        "obs_grouped": obs_grouped,
        "source_observations": source_obs,
        "reports": patient.reports.order_by("-report_date", "-created_at"),
        "treatments": patient.treatments.order_by("-start_date", "-pk"),
        "clinical_notes": patient.clinical_notes.select_related("author").order_by("-note_date"),
        "timeline_events": timeline_for_patient(patient),
        "clinical_note_form": note_form,
    }
    return render(request, "patients/workspace.html", ctx)
