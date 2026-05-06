from django.urls import path

from patients import views

app_name = "patients"

urlpatterns = [
    path("patients/", views.patient_list, name="list"),
    path("patients/<int:pk>/workspace/", views.workspace, name="workspace"),
]
