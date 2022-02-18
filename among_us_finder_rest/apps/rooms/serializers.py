from rest_framework import serializers

from among_us_finder_rest.apps.rooms.models import Room, Message
from among_us_finder_rest.apps.users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    # author = serializers.UserSerializer(many=False, slug_field='username', read_only=True)
    # author = UserSerializer(many=False)

    class Meta:
        model = Message
        fields = ["author", "comment", "published", 'room']

    def validate(self, attrs):
        if attrs.get('author') not in attrs.get('room').participants.all():
            raise serializers.ValidationError(
                {'author': 'Nie możesz napisać komentarza w pokoju, w którym nie jesteś'}
            )
        return super().validate(attrs)


class RoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, required=False)
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', "game_start", "level", "map", "players_number", "searched_players_number", "comment",
                  "participants", "host", 'messages']
