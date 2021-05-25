from rest_framework import serializers
from among_us_finder_rest.apps.room.models import Room, Message


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', "game_start", "level", "map", "players_number", "searched_players_number", "comment", "participants", "host"]
