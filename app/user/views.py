from django.shortcuts import render

from django.urls import reverse

from django.views.generic import FormView
from django.views import View

from django.contrib.auth.models import User

from questionnaire.models import ExtendedUser, PassedTest

from . import forms
# Create your views here.

# Я знаю про UserCreationForm) извините просто было интересно поковырять экземпляр класса User


class RegistrationFormView(FormView):
    template_name = "user/registration.html"
    form_class = forms.UserModelRegisterForm

    def form_valid(self, form):
        # TODO: redirect to tests list page
        self.success_url = reverse("user:sign_in")
        form.save()
        return super().form_valid(form)


class AccountView(View):
    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        extended_user = ExtendedUser.objects.get(user_id=user.pk)
        passed_tests = PassedTest.objects.filter(user=extended_user)
        return {
            "user": user,
            "passed_tests": passed_tests
        }

    def get(self, request, *args, **kwargs):
        return render(request, "user/account.html", self.get_context_data(*args, **kwargs))
