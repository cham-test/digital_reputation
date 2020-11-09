from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView

from . import forms
# Create your views here.

# Я знаю про UserCreationForm) извините просто было интересно поковырять экземпляр класса User


class RegistrationFormView(FormView):
    template_name = "registration/registration.html"
    form_class = forms.UserModelForm

    def form_valid(self, form):
        # TODO: redirect to tests list page
        self.success_url = reverse("user:sign_in")
        form.save()
        return super().form_valid(form)
