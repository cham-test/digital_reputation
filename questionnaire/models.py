from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.


class Test(models.Model):
    name = models.CharField(max_length=30, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание")

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"


class ExtendedUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    tests = models.ManyToManyField(Test, verbose_name="Тесты")


class PassedTest(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    num_of_points = models.IntegerField(default=0)


class Questions(models.Model):
    test = models.ManyToManyField(Test, verbose_name="Тесты")
    text = models.TextField(max_length=500, verbose_name="Вопрос")


class Answer(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, verbose_name="Вопрос")
    text = models.TextField(max_length=200, verbose_name="Вариант ответа")
    is_correct = models.BooleanField(default=False)

