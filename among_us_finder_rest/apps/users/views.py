from rest_framework import viewsets

from among_us_finder_rest.apps.users.models import User
from among_us_finder_rest.apps.users.serializers import UserSerializer


class UserViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
