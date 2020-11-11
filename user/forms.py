from django import forms
from django.contrib.auth.models import User
from questionnaire.models import ExtendedUser

class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "password"]

        widgets = {
            "password": forms.PasswordInput()
        }

    def save(self, commit=True):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user = User.objects.create(email=email,
                                   username=email)
        user.set_password(password)
        user.save()
        extended_user = ExtendedUser.objects.create(user=user)
        extended_user.save()
        return user
