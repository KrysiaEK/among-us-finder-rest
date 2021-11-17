from rest_framework import serializers
from among_us_finder_rest.apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'level_of_advancement']

    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed'
    )

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)
