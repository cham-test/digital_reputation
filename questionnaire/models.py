from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
# Create your models here.


class Test(models.Model):
    name = models.CharField(max_length=30, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание")

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def get_absolute_url(self):
        return reverse("questionnaire:test-detail", args=[self.pk])


class ExtendedUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    tests = models.ManyToManyField(Test, verbose_name="Тесты")


class Question(models.Model):
    test = models.ManyToManyField(Test, verbose_name="Тесты")
    text = models.TextField(max_length=500, verbose_name="Вопрос")

    def get_absolute_url(self):
        return reverse("questionnaire:question-detail", args=[self.pk])


class PassedTest(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    num_of_points = models.IntegerField(default=0)
    is_done = models.BooleanField(default=False)
    last_question = models.ForeignKey(Question, models.CASCADE, null=True)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Вопрос")
    text = models.TextField(max_length=200, verbose_name="Вариант ответа")
    is_correct = models.BooleanField(default=False)


class PassedQuestion(models.Model):
    class AnswerType(models.IntegerChoices):
        CORRECT = 2
        PARTIALLY = 1
        INCORRECT = 0

    answer_type = models.IntegerField(choices=AnswerType.choices, default=0)
    user = models.ForeignKey(ExtendedUser, models.CASCADE)
    test = models.ForeignKey(Test, models.CASCADE)
    question = models.ForeignKey(Question, models.CASCADE)

