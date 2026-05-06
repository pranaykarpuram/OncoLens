from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from evidence.models import Observation
from reports.forms import ObservationConfirmationFormSet, ReportIntakeForm
from reports.models import DiagnosticReport
from reports.services import apply_parse_to_report, confirm_extractions, reject_extractions


@login_required
def report_intake(request):
    intake_initial = {}
    pid = request.GET.get("patient") or ""
    if pid.isdigit():
        intake_initial["patient"] = int(pid)

    if request.method == "POST":
        form = ReportIntakeForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            dr = form.save(commit=False)
            dr.raw_text = form.cleaned_data["normalized_text"]
            dr.title = form.cleaned_data["computed_title"]
            dr.uploaded_by = request.user
            dr.parse_status = "pending"
            dr.save()
            apply_parse_to_report(dr)
            messages.success(request, "Report saved. Extractions generated from pasted text pending confirmation.")
            return redirect("reports:review_extraction", pk=dr.pk)
    else:
        form = ReportIntakeForm(user=request.user, initial=intake_initial)
    return render(request, "reports/intake.html", {"form": form})


@login_required
def review_extraction(request, pk):
    report = get_object_or_404(DiagnosticReport, pk=pk)
    queryset = Observation.objects.filter(report=report).order_by("pk")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "reject_all":
            reject_extractions(report)
            messages.warning(request, "Extractions rejected for this report.")
            return redirect("patients:workspace", pk=report.patient_id)

        formset = ObservationConfirmationFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            if action == "confirm_all":
                confirm_extractions(report, request.user)
                messages.success(
                    request,
                    "Confirmations recorded and source-backed observations refreshed for clinician review.",
                )
                return redirect("patients:workspace", pk=report.patient_id)
            messages.success(request, "Extraction rows updated.")
            return redirect("reports:review_extraction", pk=report.pk)

    formset = ObservationConfirmationFormSet(queryset=queryset)

    return render(
        request,
        "reports/extraction_review.html",
        {"report": report, "formset": formset},
    )


@login_required
def confirm_extraction(request, pk):
    if request.method != "POST":
        return redirect("reports:review_extraction", pk=pk)
    report = get_object_or_404(DiagnosticReport, pk=pk)
    queryset = Observation.objects.filter(report=report).order_by("pk")
    formset = ObservationConfirmationFormSet(request.POST, queryset=queryset)
    if formset.is_valid():
        formset.save()
    confirm_extractions(report, request.user)
    messages.success(request, "Extractions confirmed.")
    return redirect("patients:workspace", pk=report.patient_id)
