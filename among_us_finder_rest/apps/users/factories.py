import factory

from among_us_finder_rest.apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: '%s@example.com' % o.username)

    class Meta:
        model = User
