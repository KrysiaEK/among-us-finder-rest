from django.db import models
from among_us_finder_rest.apps.room.constants import MapChoices, LevelChoices
from django.core.validators import MaxValueValidator, MinValueValidator


class Room(models.Model):
    name = models.CharField(max_length=20, blank=True)
    game_start = models.DateTimeField()
    level = models.PositiveSmallIntegerField(choices=LevelChoices.Choices)
    map = models.PositiveSmallIntegerField(choices=MapChoices.Choices, null=True, blank=True)
    players_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(4), MaxValueValidator(10)])
    searched_players_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])
    comment = models.TextField(blank=True)
    participants = models.ManyToManyField('users.User')
    host = models.ForeignKey('users.User', blank=False, null=True, on_delete=models.SET_NULL, related_name='host')


class Message(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    comment = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
