from rest_framework import serializers
from among_us_finder_rest.apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'level_of_advancement']
