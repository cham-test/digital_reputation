from django.shortcuts import get_object_or_404, render, redirect, HttpResponse

from django.urls import reverse

from django.views.generic import ListView, DetailView
from django.views.decorators.csrf import csrf_exempt

from django.db.models import QuerySet

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils.decorators import method_decorator

from .models import Test, Question, Answer, PassedTest, ExtendedUser, PassedQuestion
# Create your views here.


class TestListView(ListView):
    model = Test
    context_object_name = "tests"
    template_name = "questionnaire/tests_list.html"


class PointsCalculatorMixin:
    @property
    def test_max_points(self) -> int:
        """calculate the maximum score for the test"""
        questions = Question.objects.filter(test=self.kwargs["test_pk"])
        sum_points = questions.count() * 10
        return sum_points

    @property
    def has_many_correct_answers(self) -> bool:
        count_correct_answers: int = Answer.objects.filter(
            question=self.kwargs["question_pk"], is_correct=True).count()
        return True if count_correct_answers > 1 else False

    def calculate_points_from_answer(self) -> int:
        answers_data = self.request.POST.getlist("answer_pk")
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

    @property
    def calculate_percent(self) -> int:
        max_points = self.test_max_points
        points_scored = PassedTest.objects.get(test_id=self.kwargs["test_pk"]).num_of_points
        return int(points_scored * 100 / max_points)

    @property
    def test_result(self) -> bool:
        return True if self.calculate_percent > 70 else False

    def add_points_to_passed_test(self, **kwargs) -> PassedTest:
        num_of_points = PassedTest.objects.get(user=self.get_extended_user(),
                                               test=self.kwargs["test_pk"]).num_of_points
        get_points_from_question = self.calculate_points_from_answer()
        add_points = num_of_points + get_points_from_question
        passed_test = PassedTest.objects.update(user=self.get_extended_user(),
                                                test=self.kwargs["test_pk"],
                                                num_of_points=add_points)
        return passed_test


class ExtendedUserMixin:
    def get_extended_user(self) -> ExtendedUser:
        user_id = User.objects.get(username=self.request.user)
        extended_user = ExtendedUser.objects.get(user_id=user_id)
        return extended_user


class PassedTestMixin:
    def delete_passed_test(self) -> tuple:
        passed_test = PassedTest.objects.get(user=self.get_extended_user(),
                                             test_id=self.kwargs["test_pk"]).delete()
        self.delete_passed_questions()
        return passed_test

    def delete_passed_questions(self) -> tuple:
        passed_question = PassedQuestion.objects.filter(user=self.get_extended_user(),
                                                        test_id=self.kwargs["test_pk"]).delete()
        return passed_question

    def get_passed_test_status(self) -> str:
        user = self.get_extended_user()
        try:
            test = PassedTest.objects.get(user=user, test_id=self.kwargs["test_pk"])
            if test.is_done:
                return "completed"
            return "started"

        except ObjectDoesNotExist:
            return "not_started"

    def start_test(self) -> PassedTest:
        passed_test = PassedTest.objects.create(user=self.get_extended_user(),
                                                test_id=self.kwargs["test_pk"],
                                                last_question_id=1)
        passed_test.save()
        return passed_test

    def continue_test(self):
        try:
            passed_test = PassedTest.objects.update(user=self.get_extended_user(),
                                                    test_id=self.kwargs["test_pk"],
                                                    last_question_id=self.kwargs["question_pk"] + 1)
            return passed_test
        except IntegrityError:
            pass

    @property
    def is_passed_test(self) -> bool:
        try:
            questions_count: int = Question.objects.filter(test=self.kwargs["test_pk"]).count()
            passed_question = PassedQuestion.objects.get(test_id=self.kwargs["test_pk"],
                                                         question_id=questions_count,
                                                         user=self.get_extended_user())
            return True
        except ObjectDoesNotExist:
            return False

    def mark_test_as_passed(self) -> PassedTest:
        passed_test = PassedTest.objects.update(user=self.get_extended_user(),
                                                test_id=self.kwargs["test_pk"],
                                                is_done=True)
        return passed_test


class TestDetailView(LoginRequiredMixin, DetailView, PointsCalculatorMixin, PassedTestMixin, ExtendedUserMixin):
    model = Test
    template_name = "questionnaire/tests_detail.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TestDetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        test_status = self.get_passed_test_status()
        if test_status == "completed":
            context["percent"] = self.calculate_percent
            context["test_result"] = self.test_result
        context["test_status"] = test_status
        return render(request, self.template_name, context)

    def delete(self, request, *args, **kwargs):
        self.delete_passed_test()
        return HttpResponse("OK")

    def get_context_data(self, **kwargs):
        test = get_object_or_404(Test, pk=self.kwargs["test_pk"])
        questions = Question.objects.filter(test=self.kwargs["test_pk"])
        max_points = self.test_max_points


        return {
            "test": test,
            "questions": questions,
            "max_points": max_points
        }


class QuestionMixin:
    def get_last_question(self) -> int:
        passed_test = PassedTest.objects.get(user=self.get_extended_user(),
                                             test_id=self.kwargs["test_pk"])
        return passed_test.last_question.pk

    def redirect_to_last_question(self) -> redirect:
        return redirect(reverse("questionnaire:question-detail", kwargs={
            "test_pk": self.kwargs["test_pk"],
            "question_pk": self.get_last_question()
        }))

    def add_passed_question(self) -> PassedQuestion:
        answer_points = self.calculate_points_from_answer()
        if answer_points == 10:
            answer_type = 2
        elif answer_points == 0:
            answer_type = 0
        else:
            answer_type = 1
        passed_question = PassedQuestion.objects.create(test_id=self.kwargs["test_pk"],
                                                        question_id=self.kwargs["question_pk"],
                                                        user=self.get_extended_user(),
                                                        answer_type=answer_type)
        passed_question.save()
        return passed_question


class QuestionDetailView(LoginRequiredMixin, DetailView, PointsCalculatorMixin,
                         ExtendedUserMixin, PassedTestMixin, QuestionMixin):
    model = Question
    context_object_name = "question"
    template_name = "questionnaire/question_detail.html"

    def get(self, request, *args, **kwargs):
        test_status = self.get_passed_test_status()

        if test_status == "started":
            if self.get_last_question() != self.kwargs["question_pk"]:
                return self.redirect_to_last_question()
            return render(request, self.template_name, self.get_context_data(**kwargs))

        if test_status == "completed":
            return redirect(reverse("questionnaire:test-result", args=[self.kwargs["test_pk"]]))

        else:
            self.start_test()
            return render(request, self.template_name, context=self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        answer_pks = request.POST.get("answer_pk")
        if answer_pks:
            self.add_passed_question()
            self.add_points_to_passed_test()
            self.continue_test()
            return redirect(self.get_next_page())
        else:
            return self.redirect_to_last_question()

    def get_context_data(self, **kwargs):
        question = get_object_or_404(Question, test=kwargs["test_pk"], pk=kwargs["question_pk"])
        answers: QuerySet = Answer.objects.filter(question=question)
        return {
            "test": question.test,
            "question": question,
            "answers": answers,
            "has_many_correct_answers": self.has_many_correct_answers,
            "next_page": self.get_next_page()
        }

    def get_next_page(self) -> str:
        try:
            next_question = Question.objects.get(pk=self.kwargs["question_pk"] + 1)
            return reverse("questionnaire:question-detail", kwargs={
                "test_pk": self.kwargs["test_pk"],
                "question_pk": next_question.pk
            })
        except ObjectDoesNotExist:
            return reverse("questionnaire:test-result", args=[self.kwargs["test_pk"]])


class TestResultView(DetailView, ExtendedUserMixin, PassedTestMixin,
                     QuestionMixin, PointsCalculatorMixin):
    def get(self, request, *args, **kwargs):
        if self.is_passed_test:
            self.mark_test_as_passed()
            return render(request, "questionnaire/test_result.html", self.get_context_data())

        try:
            return self.redirect_to_last_question()

        except ObjectDoesNotExist:
            return redirect(reverse("questionnaire:test-detail",
                                    kwargs={"test_pk": self.kwargs["test_pk"]}))

    def get_context_data(self, **kwargs):
        test = Test.objects.get(pk=self.kwargs["test_pk"])
        passed_test = PassedTest.objects.get(test_id=self.kwargs["test_pk"],
                                             user=self.get_extended_user())
        passed_questions = PassedQuestion.objects.filter(test_id=self.kwargs["test_pk"],
                                                         user=self.get_extended_user())
        return {
            "test": test,
            "passed_test": passed_test,
            "passed_questions": passed_questions,
            "percent": self.calculate_percent,
            "test_result": self.test_result
        }
