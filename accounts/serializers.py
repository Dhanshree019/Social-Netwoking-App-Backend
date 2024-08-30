from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.contrib.auth.models import User

from accounts.models import FriendRequest


# User model serializer
class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')


# FriendRequest model serializer
class PendingFriendRequestSerializer(ModelSerializer):

    sender = SerializerMethodField('get_sender')


    class Meta:
        model = FriendRequest
        fields = ('id', 'sender', 'created_at', 'updated_at')

    @staticmethod
    def get_sender(obj):
        return {
            "id": obj.sender.id,
            "first_name": obj.sender.first_name,
            "last_name": obj.sender.last_name,
            "email": obj.sender.email
        }



