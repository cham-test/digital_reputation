from django import forms
from django.contrib.auth.models import User
from questionnaire.models import ExtendedUser


class UserModelRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "password"]

        widgets = {
            "password": forms.PasswordInput()
        }


