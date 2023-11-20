from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import permissions
from rest_framework.decorators import action

from .serializers import CustomUserSerializer

User = get_user_model()


class CustomUserView(UserViewSet):
    http_method_names = ['get', 'post']
    permission_classes = [permissions.AllowAny, ]
    serializer_class = CustomUserSerializer

    @action(
        ["get"], detail=False,
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)

    def reset_password(self, request, *args, **kwargs):
        pass

    def reset_password_confirm(self, request, *args, **kwargs):
        pass

    def set_username(self, request, *args, **kwargs):
        pass

    def reset_username(self, request, *args, **kwargs):
        pass

    def reset_username_confirm(self, request, *args, **kwargs):
        pass

    def resend_activation(self, request, *args, **kwargs):
        pass

    def activation(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        pass
