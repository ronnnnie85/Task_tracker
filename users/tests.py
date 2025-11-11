from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationViewTests(APITestCase):
    """Тесты регистрации пользователя через API."""

    def test_register_user(self):
        url = "/users/auth/register/"
        data = {
            "email": "user@example.com",
            "password": "strongpassword",
            "phone": "+70000000000",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, data["email"])


class UserDetailViewTests(APITestCase):
    """Тесты просмотра и обновления профиля пользователя."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            phone="+70000000000",
        )

        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        url = "/users/profile/"
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_profile(self):
        url = "/users/profile/"
        data = {
            "phone": "+79999999999",
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79999999999")
