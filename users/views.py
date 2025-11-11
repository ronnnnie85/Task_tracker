from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from .serializers import UserRegistrationSerializer, UserUpdateSerializer

User = get_user_model()


class RegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя."""

    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование своего профиля."""

    serializer_class = UserUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Возвращает текущего пользователя."""

        return self.request.user
