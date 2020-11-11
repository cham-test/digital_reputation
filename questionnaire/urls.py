from django.urls import path

from . import views

app_name = "questionnaire"

urlpatterns = [
    path("list/", views.TestListView.as_view(), name="test-list"),
    path("detail/<int:pk>/", views.TestDetailView.as_view(), name="test-detail"),
    path("detail/<int:pk>/result/", views.TestResultView.as_view(), name="test-result"),
    path("detail/<int:test_pk>/question/<int:question_pk>/",
         views.QuestionDetailView.as_view(), name="question-detail"),
]
