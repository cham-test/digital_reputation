from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin


from .models import Test, Question, Answer, PassedTest
# Create your views here.


class TestListView(ListView):
    model = Test
    context_object_name = "tests"
    template_name = "tests/list.html"


# class PointsCalculatorMixin(ContextMixin):
#     @property
#     def test_max_points(self) -> int:
#         questions = Question.objects.filter(test=self.kwargs["pk"])
#         sum_points = questions.count() * 10
#         return sum_points


class TestDetailView(DetailView):
    model = Test
    context_object_name = "test"
    template_name = "tests/detail.html"

    def get_context_data(self, **kwargs):
        questions = Question.objects.filter(test=self.kwargs["pk"])
        return {
            "questions": questions
        }


