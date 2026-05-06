from django.urls import path

from briefs import views

app_name = "briefs"

urlpatterns = [
    path("tumor-board/", views.tumor_board, name="tumor_board"),
]
