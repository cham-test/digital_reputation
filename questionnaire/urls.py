from django.urls import path

from . import views

app_name = "questionnaire"

urlpatterns = [
    path("list/", views.TestListView.as_view(), name="test-list"),
    path("detail/<int:pk>/", views.TestDetailView.as_view(), name="test-detail")
]