from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from evidence.search import search_evidence


@login_required
def search_view(request):
    q = request.GET.get("q", "").strip()
    patient_id_raw = request.GET.get("patient")
    filters = {}
    if patient_id_raw and patient_id_raw.isdigit():
        filters["patient"] = int(patient_id_raw)
    rows = search_evidence(q, filters) if q else []

    hydrated = []
    for row in rows:
        hydrated.append({**row, "patient_display": row["patient"].full_name, "patient_id": row["patient"].pk})

    return render(
        request,
        "evidence/search.html",
        {"results": hydrated, "q": q, "patient_filter": patient_id_raw or ""},
    )
