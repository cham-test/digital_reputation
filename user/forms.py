from django import forms
from django.contrib.auth.models import User


class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "password"]

        widgets = {
            "password": forms.PasswordInput()
        }

    def save(self, commit=True):
        print(self.cleaned_data)
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user = User.objects.create(email=email,
                                   username=email)
        user.set_password(password)
        user.save()
        return user
