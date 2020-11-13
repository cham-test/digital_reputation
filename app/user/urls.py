from django.urls import path

from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = "user"

urlpatterns = [
    # не думаю что в рамках тестового задания нужно что то переопределять в этих классах
    path("sign_in/", LoginView.as_view(template_name="user/login.html"), name="sign_in"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("sign_up/", views.RegistrationFormView.as_view(), name="sign_up")
]