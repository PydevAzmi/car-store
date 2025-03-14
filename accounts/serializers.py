from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, CurrentPasswordSerializer

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'phone_number', 'username', 'password', 'gender')
