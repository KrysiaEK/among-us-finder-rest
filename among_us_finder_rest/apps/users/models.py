from django.db import models
from django.contrib.auth.models import AbstractUser

from among_us_finder_rest.apps.users.constants import LevelOfAdvancement


class User(AbstractUser):
    level_of_advancement = models.PositiveSmallIntegerField(
        choices=LevelOfAdvancement.Choices, default=LevelOfAdvancement.BEGINNER
    )
