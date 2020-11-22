from django.shortcuts import render, redirect, HttpResponse

from django.urls import reverse

from django.views.generic import FormView
from django.views import View

from django.contrib.auth.models import User

from django.core.mail import send_mail

from django.conf import settings

from questionnaire.models import ExtendedUser, PassedTest
from questionnaire.views import ExtendedUserMixin

from . import forms
# Create your views here.

# Я знаю про UserCreationForm) извините просто было интересно поковырять экземпляр класса User


class RegistrationFormView(FormView, ExtendedUserMixin):
    template_name = "user/registration.html"
    form_class = forms.UserModelRegisterForm

    def send_activation_code(self, user_email: str):
        user = User.objects.get(email=user_email)
        activation_code = ExtendedUser.objects.get(user=user).activation_code
        link_url = settings.DOMAIN_NAME + reverse('user:email_confirmation')
        query_params = f"?username={user_email}&activation_code={activation_code}"
        message = "For activation you account follow to link: " \
                  "<br>" \
                  f"<a href='{link_url}{query_params}'> Link </a>"
        return send_mail("Activation code", "", "romanshapran96@gmail.com",
                         [user_email], html_message=message, fail_silently=False)

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = User.objects.create(email=email,
                                   username=email,
                                   is_active=False)
        user.set_password(password)
        user.save()
        extended_user = ExtendedUser.objects.create(user=user,
                                                    activation_code=self.generate_activation_code())
        extended_user.save()
        self.send_activation_code(user.email)
        self.success_url = reverse("user:email_confirmation")
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


class EmailConfirmationView(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get("username")
        activation_code = request.GET.get("activation_code")
        if username and activation_code:
            user = User.objects.get(username=username)
            extended_user = ExtendedUser.objects.get(user=user)
            if extended_user.activation_code == activation_code:
                user.is_active = True
                user.save()
                return redirect(reverse("user:sign_in"))

            return HttpResponse("Invalid activation code")

        return render(request, "user/email_confirmation.html", {})