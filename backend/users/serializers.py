from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import User


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        source='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()
