from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'email', 'password']