from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from briefs.models import TumorBoardBrief
from briefs.services import generate_tumor_board_brief
from patients.models import Patient


@login_required
def tumor_board(request):
    selected_id_raw = (
        request.POST.get("patient_id") if request.method == "POST" else request.GET.get("patient") or ""
    )
    patient = None

    patients = Patient.objects.order_by("last_name", "first_name")

    if selected_id_raw.isdigit():
        patient = Patient.objects.filter(pk=int(selected_id_raw)).first()

    if request.method == "POST" and request.POST.get("generate"):
        if not patient:
            messages.error(request, "Pick a patient first.")
            return redirect("briefs:tumor_board")
        generate_tumor_board_brief(patient, user=request.user)
        messages.success(request, "Brief generated from source-backed chart data.")
        return redirect(f"/tumor-board/?patient={patient.pk}")

    brief = None
    if patient:
        brief = TumorBoardBrief.objects.filter(patient=patient).order_by("-created_at").first()

    return render(
        request,
        "briefs/tumor_board.html",
        {"patients": patients, "selected_patient": patient, "brief": brief},
    )
