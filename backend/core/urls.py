from django.urls import path

from core import api_views
from core import views as core_views

app_name = "core"

urlpatterns = [
    path("queue/", core_views.review_queue, name="review_queue"),
    path("admin-panel/", core_views.operations_dashboard, name="admin_panel"),
    path("api/auth/login/", api_views.api_auth_login, name="api_auth_login"),
    path("api/auth/logout/", api_views.api_auth_logout, name="api_auth_logout"),
    path("api/auth/session/", api_views.api_auth_session, name="api_auth_session"),
    path("api/review-queue/", api_views.api_review_queue, name="api_review_queue"),
    path("api/patients/", api_views.api_patients_search, name="api_patients_search"),
    path("api/reports/intake/", api_views.api_report_intake_json, name="api_report_intake_json"),
    path("api/admin/summary/", api_views.api_admin_summary, name="api_admin_summary"),
    path("api/patients/<int:pk>/evidence/", api_views.api_patient_evidence, name="api_patient_evidence"),
    path(
        "api/patients/<int:pk>/mark-reviewed/",
        api_views.api_patient_mark_reviewed,
        name="api_patient_mark_reviewed",
    ),
    path("api/evidence/search/", api_views.api_evidence_search, name="api_evidence_search"),
    path("api/reports/<int:pk>/extract/", api_views.api_report_extract, name="api_report_extract"),
    path("api/patients/<int:pk>/brief/", api_views.api_patient_brief, name="api_patient_brief"),
]
