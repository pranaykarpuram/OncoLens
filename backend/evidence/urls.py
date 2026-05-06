from django.urls import path

from evidence import views

app_name = "evidence"

urlpatterns = [
    path("search/", views.search_view, name="search"),
]
