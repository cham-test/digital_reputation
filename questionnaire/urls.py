from django.urls import path

from . import views

app_name = "questionnaire"

urlpatterns = [
    path("list/", views.TestListView.as_view(), name="list"),
]