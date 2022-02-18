from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from among_us_finder_rest.apps.rooms.utilities import send_mail_to_admins
from among_us_finder_rest.apps.rooms.models import Room, Message
from among_us_finder_rest.apps.rooms.serializers import RoomSerializer, MessageSerializer
from among_us_finder_rest.apps.users.models import User



class RoomViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    """View to create, join, leave room. Allows also remove participants or report abuse"""

    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['game_start', 'map', 'level', 'players_number']
    ordering_fields = ['game_start', 'level', 'players_number']


    def perform_create(self, serializer):
        room = serializer.save()
        room.participants.add(self.request.user)

    def create(self, request, *args, **kwargs):
        data = {
            'host': self.request.user.id,
            **request.data
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['PUT'])
    def join(self, request, **kwargs):
        room = self.get_object()
        if self.request.user in room.participants.all():
            return Response('You have already joined this room',
                            status=status.HTTP_400_BAD_REQUEST)
        room.participants.add(self.request.user)
        return Response({'status': 'joined the room'})

    @action(detail=True, methods=['DELETE'])
    def leave(self, request, **kwargs):
        room = self.get_object()
        if self.request.user in room.participants.all():
            room.participants.remove(self.request.user)
            return Response({'status': 'you left the room'})
        else:
            return Response('You are not in this room!',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def remove_participant(self, request, *args, **kwargs):
        room = self.get_object()
        user_to_be_removed = get_object_or_404(User, id=request.data.get('user_id'))
        if self.request.user == room.host:
            if user_to_be_removed in room.participants.all():
                room.participants.remove(user_to_be_removed)
                return Response({'status': 'participant deleted'})
            else:
                return Response('This user is not in this room!',
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('You no host!',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def report_user(self, request, *args, **kwargs):
        reporting_user = self.request.user
        reported_user = get_object_or_404(User, id=request.data.get('reported_user_id'))
        comment = request.data.get('comment')
        message = f'User {reporting_user.id} reported user {reported_user.id} because {comment}'
        send_mail_to_admins(message)
        return Response(status=status.HTTP_200_OK)


class MessageViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    """View to create messages"""

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    #  permission_classes =

    #  aby sprawdzało we wszystkuch stronach czy user jest zalogowany muszę mieć coś tam w settingsach, a potem jeśli
    #  chcę na jakichś stronach aby nie był zalogowany to muszę zrobić perrimission classes i dać np. że wszyscy mogą

    def create(self, request, *args, **kwargs):
        data = {
            'author': request.user.id,
            'published': timezone.now(),
            **request.data
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
