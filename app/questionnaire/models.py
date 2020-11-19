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

    def __str__(self):
        return self.name


class ExtendedUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    tests = models.ManyToManyField(Test, verbose_name="Тесты")
    activation_code = models.CharField(max_length=120, verbose_name="Код авторизации почты")

    class Meta:
        verbose_name = "Расширенный пользователь"
        verbose_name_plural = "Расширенные пользователи"

    def __str__(self):
        return self.user.username


class Question(models.Model):
    test = models.ManyToManyField(Test, verbose_name="Тесты")
    text = models.TextField(max_length=500, verbose_name="Вопрос")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def get_absolute_url(self):
        return reverse("questionnaire:question-detail", args=[self.pk])

    def __str__(self):
        return self.text


class PassedTest(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    num_of_points = models.IntegerField(default=0)
    is_done = models.BooleanField(default=False)
    last_question = models.ForeignKey(Question, models.CASCADE, null=True)

    class Meta:
        verbose_name = "Пройденный тест"
        verbose_name_plural = "Пройденные тесты"

    def __str__(self):
        return f"{self.user.user.username}: {self.test.name}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Вопрос")
    text = models.TextField(max_length=200, verbose_name="Вариант ответа")
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return self.text


class PassedQuestion(models.Model):
    class AnswerType(models.IntegerChoices):
        CORRECT = 2
        PARTIALLY = 1
        INCORRECT = 0

    answer_type = models.IntegerField(choices=AnswerType.choices, default=0)
    user = models.ForeignKey(ExtendedUser, models.CASCADE)
    test = models.ForeignKey(Test, models.CASCADE)
    question = models.ForeignKey(Question, models.CASCADE)

    class Meta:
        verbose_name = "Пройденный вопрос"
        verbose_name_plural = "Пройденные вопросы"

    def __str__(self):
        return f"{self.user.user.username}: {self.test}"
