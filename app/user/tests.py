from django.test import TestCase

from django.urls import reverse

from django.contrib.auth.models import User

from questionnaire.models import ExtendedUser

# Create your tests here.


class UserTests(TestCase):
    def user_registration(self):
        response = self.client.post(reverse("user:sign_up"), data={"email": "some@mail.xd",
                                                                   "password": "password"})
        user = User.objects.get(username="some@mail.xd")
        self.assertEqual(user.username, user.email)
        extended_user = ExtendedUser.objects.get(user=user)
        self.assertEqual(extended_user.user, user)

        self.assertEqual(response.url, reverse("user:sign_in"))
        self.assertEqual(response.status_code, 302)

    def user_login(self):
        response = self.client.post(reverse("user:sign_in"), data={"username": "some@mail.xd",
                                                                   "password": "password"},
                                    follow=True)
        self.assertEqual(response.context["user"].username, "some@mail.xd")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, response.redirect_chain)

    def test_redirect_if_not_login(self):
        request_url = reverse("questionnaire:test-detail", args=[1])
        response = self.client.get(request_url)
        self.assertRedirects(response, f"{reverse('user:sign_in')}?next={request_url}")

    def test_register_and_login_logout(self):
        self.user_registration()
        self.user_login()
