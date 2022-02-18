import factory
from django.utils import timezone
from factory.fuzzy import FuzzyChoice, FuzzyInteger

from among_us_finder_rest.apps.rooms.constants import LevelChoices, MapChoices
from among_us_finder_rest.apps.rooms.models import Room
from among_us_finder_rest.apps.users.factories import UserFactory


class RoomFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Room %d' % n)
    game_start = factory.LazyFunction(timezone.now)
    level = LevelChoices.BEGINNER
    map = MapChoices.THE_SKELD
    players_number = FuzzyInteger(1, 10)
    searched_players_number = 8
    comment = "hej"
    host = factory.SubFactory(UserFactory)

    class Meta:
        model = Room
