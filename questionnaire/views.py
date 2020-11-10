from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin


from .models import Test, Question, Answer, PassedTest
# Create your views here.


class TestListView(ListView):
    model = Test
    context_object_name = "tests"
    template_name = "questionnaire/tests/list.html"


class PointsCalculatorMixin(ContextMixin):
    @property
    def test_max_points(self) -> int:
        """calculate the maximum score for the test"""
        questions = Question.objects.filter(test=self.kwargs["pk"])
        sum_points = questions.count() * 10
        return sum_points


class TestDetailView(DetailView, PointsCalculatorMixin):
    model = Test
    context_object_name = "test"
    template_name = "questionnaire/tests/detail.html"

    def get_context_data(self, **kwargs):
        questions = Question.objects.filter(test=self.kwargs["pk"])
        max_points = self.test_max_points
        return {
            "questions": questions,
            "max_points": max_points
        }


class QuestionView(DetailView):
    model = Question
    template_name = ""