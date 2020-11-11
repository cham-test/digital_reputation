from django.shortcuts import get_object_or_404, render, redirect

from django.urls import reverse

from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin

from django.db.models import QuerySet

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from django.contrib.auth.models import User

from .models import Test, Question, Answer, PassedTest, ExtendedUser, PassedQuestion
# Create your views here.


class TestListView(ListView):
    model = Test
    context_object_name = "tests"
    template_name = "questionnaire/tests_list.html"


class PointsCalculatorMixin(ContextMixin):
    @property
    def test_max_points(self) -> int:
        """calculate the maximum score for the test"""
        questions = Question.objects.filter(test=self.kwargs["pk"])
        sum_points = questions.count() * 10
        return sum_points

    @property
    def has_many_correct_answers(self) -> bool:
        count_correct_answers: int = Answer.objects.filter(
            question=self.kwargs["question_pk"], is_correct=True).count()
        return True if count_correct_answers > 1 else False

    def calculate_points_from_answer(self, request) -> int:
        answers_data = request.POST.getlist("answer_pk")
        print(answers_data)
        if self.has_many_correct_answers:
            result: int = 0
            answers = Answer.objects.filter(
                question=self.kwargs["question_pk"]
            )
            answer_correct_weight = 10 / answers.filter(is_correct=True).count()
            for answer_pk in answers_data:
                if Answer.objects.get(pk=answer_pk).is_correct:
                    result += answer_correct_weight
                else:
                    result -= answer_correct_weight
            return int((result > 0) * result)

        return 10 if Answer.objects.get(pk=answers_data[0]).is_correct else 0

    def add_points_to_passed_test(self, request, **kwargs):
        num_of_points = PassedTest.objects.get(user=self.get_extended_user(request),
                                               test=self.kwargs["test_pk"]).num_of_points
        get_points_from_question = self.calculate_points_from_answer(request)
        add_points = num_of_points + get_points_from_question
        PassedTest.objects.update(user=self.get_extended_user(request),
                                  test=self.kwargs["test_pk"],
                                  num_of_points=add_points)

class ExtendedUserMixin:
    def get_extended_user(self, request, **kwargs) -> ExtendedUser:
        user_id = User.objects.get(username=request.user)
        extended_user = ExtendedUser.objects.get(user_id=user_id)
        return extended_user


class TestDetailView(DetailView, PointsCalculatorMixin):
    model = Test
    template_name = "questionnaire/tests_detail.html"

    def get_context_data(self, **kwargs):
        test = get_object_or_404(Test, pk=self.kwargs["pk"])
        questions = Question.objects.filter(test=self.kwargs["pk"])
        max_points = self.test_max_points
        return {
            "test": test,
            "questions": questions,
            "max_points": max_points
        }


class QuestionDetailView(DetailView, PointsCalculatorMixin, ExtendedUserMixin):
    model = Question
    context_object_name = "question"
    template_name = "questionnaire/question_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            passed_test = PassedTest.objects.get(user=self.get_extended_user(request))

            if passed_test.is_done:
                return redirect(reverse("questionnaire:test-result", args=[self.kwargs["test_pk"]]))

            if self.kwargs["question_pk"] is not self.get_last_question(request):
                return redirect(reverse("questionnaire:question-detail", kwargs={
                    "test_pk": self.kwargs["test_pk"],
                    "question_pk": self.get_last_question(request)
                }))

            return render(request, self.template_name, context=self.get_context_data(**kwargs))

        except ObjectDoesNotExist:
            self.start_test(request, *args, **kwargs)
            return render(request, self.template_name, context=self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        self.add_passed_question(request)
        self.add_points_to_passed_test(request)
        self.continue_test(request, *args, **kwargs)
        return redirect(self.get_next_page(*args, **kwargs))

    def get_context_data(self, **kwargs):
        question = get_object_or_404(Question, test=kwargs["test_pk"], pk=kwargs["question_pk"])
        answers: QuerySet = Answer.objects.filter(question=question)
        return {
            "test": question.test,
            "question": question,
            "answers": answers,
            "has_many_correct_answers": self.has_many_correct_answers,
            "next_page": self.get_next_page(**kwargs)
        }

    def start_test(self, request, *args, **kwargs):
        passed_test = PassedTest.objects.create(user=self.get_extended_user(request),
                                                test_id=self.kwargs["test_pk"],
                                                last_question_id=1)
        passed_test.save()

    def continue_test(self, request, *args, **kwargs):
        try:
            passed_test = PassedTest.objects.update(user=self.get_extended_user(request),
                                                    test_id=self.kwargs["test_pk"],
                                                    last_question_id=self.kwargs["question_pk"] + 1)
        except IntegrityError:
            pass

    def get_next_page(self, *args, **kwargs) -> str:
        try:
            next_question = Question.objects.get(pk=self.kwargs["question_pk"] + 1)
            return reverse("questionnaire:question-detail", kwargs={
                "test_pk": self.kwargs["test_pk"],
                "question_pk": next_question.pk
            })
        except ObjectDoesNotExist:
            return reverse("questionnaire:test-result", args=[self.kwargs["test_pk"]])

    def get_last_question(self, request, ** kwargs):
        passed_test = PassedTest.objects.get(user=self.get_extended_user(request),
                                             test_id=self.kwargs["test_pk"])
        return passed_test.last_question.pk

    def add_passed_question(self, request):
        answer_points = self.calculate_points_from_answer(request)
        print(answer_points)
        if answer_points == 10:
            answer_type = 2
        elif answer_points == 0:
            answer_type = 0
        else:
            answer_type = 1
        passed_question = PassedQuestion.objects.create(test_id=self.kwargs["test_pk"],
                                                        question_id=self.kwargs["question_pk"],
                                                        user=self.get_extended_user(request),
                                                        answer_type=answer_type)
        passed_question.save()


class TestResultView(DetailView, ExtendedUserMixin):
    def get(self, request, *args, **kwargs):
        PassedTest.objects.update(user=self.get_extended_user(request),
                                  test_id=self.kwargs["pk"],
                                  is_done=True)

        test = Test.objects.get(pk=self.kwargs["pk"])
        passed_test = PassedTest.objects.get(test_id=self.kwargs["pk"],
                                             user=self.get_extended_user(request))
        passed_questions = PassedQuestion.objects.filter(test_id=self.kwargs["pk"],
                                                         user=self.get_extended_user(request))
        return render(request, "questionnaire/test_result.html", context={
            "test": test,
            "passed_test": passed_test,
            "passed_questions": passed_questions
        })



