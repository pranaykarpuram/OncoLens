from django.urls import path

from reports import views

app_name = "reports"

urlpatterns = [
    path("intake/", views.report_intake, name="intake"),
    path("reports/<int:pk>/review-extraction/", views.review_extraction, name="review_extraction"),
    path("reports/<int:pk>/confirm-extraction/", views.confirm_extraction, name="confirm_extraction"),
]
