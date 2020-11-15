import random

from django.test import TestCase, Client

from django.contrib.auth.models import User

from django.urls import reverse

from .models import Test, Question, ExtendedUser, Answer, PassedQuestion, PassedTest
# Create your tests here.


class TestsTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.create_many_tests()
        self.testing_test = Test.objects.get(id=1)
        self.create_questions_to_test_with_answers(self.testing_test)
        self.user = User.objects.create(username="some@mail.xd",
                                   email="some@mail.xd",
                                   password="password")
        self.user.set_password("password")
        self.user.save()
        self.extended_user = ExtendedUser.objects.create(user=self.user)
        self.extended_user.save()
        self.passed_test: PassedTest = self.create_passed_test_obj()
        self.client.login(username="some@mail.xd", password="password")

    def create_many_tests(self) -> None:
        for test_id in range(1, 10):
            test = Test.objects.create(name=f"Testing test #{test_id}",
                                       description=f"Test for django testing system #{test_id}")
            test.save()

    def create_passed_test_obj(self) -> PassedTest:
        passed_test = PassedTest.objects.create(user=self.extended_user,
                                                test=self.testing_test)
        passed_test.save()
        return PassedTest

    # add questions to Test with id=1 with answer
    def create_questions_to_test_with_answers(self, test: Test) -> None:
        for question_id in range(1, 5):
            question = Question.objects.create(text=f"Question with id: {question_id}")
            question.save()
            question.test.add(test)
            if question.pk % 2 == 0:
                self.create_single_correct_answer(question)
            else:
                self.create_multiple_correct_answer(question)

    def create_single_correct_answer(self, question: Question) -> None:
        answer_1 = Answer.objects.create(question=question,
                                         text="first_answer",
                                         is_correct=True)
        answer_2 = Answer.objects.create(question=question,
                                         text="second answer")
        answer_3 = Answer.objects.create(question=question,
                                         text="third answer")

    def create_multiple_correct_answer(self, question: Question):
        answer_1 = Answer.objects.create(question=question,
                                         text="first_answer",
                                         is_correct=True)
        answer_2 = Answer.objects.create(question=question,
                                         text="second answer",
                                         is_correct=True)
        answer_3 = Answer.objects.create(question=question,
                                         text="third answer")

    def test_get_tests_list_page(self):
        response = self.client.get(reverse("questionnaire:test-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object_list"].count(), 9)

    def test_get_test_detail(self):
        response = self.client.get(reverse("questionnaire:test-detail", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_question_detail_post_request(self):
        response = self.client.post(reverse("questionnaire:question-detail", kwargs={
            "test_pk": self.testing_test.pk,
            "question_pk": 1
        }), data={"answer_pk": [1, 2]})
        self.assertRedirects(response, expected_url=reverse("questionnaire:question-detail",
                                                            kwargs={
                                                                "test_pk": self.testing_test.pk,
                                                                "question_pk": 2
                                                            }))
        self.assertEqual(self.passed_test.objects.get(test=self.testing_test).num_of_points, 10)

    # TODO: добавить тесты для вычисления правильных ответов