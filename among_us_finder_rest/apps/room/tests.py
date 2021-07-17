from unittest.mock import patch

from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from among_us_finder_rest.apps.room.factories import RoomFactory
from among_us_finder_rest.apps.room.models import Room, Message
from among_us_finder_rest.apps.users.factories import UserFactory


class RoomTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.room = RoomFactory()

    def setUp(self):
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_users_list(self):
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        ids_list = [obj.get('id') for obj in data]
        self.assertIn(self.user.id, ids_list)

    def test_create_room(self):
        rooms_before = Room.objects.count()
        response = self.client.post('/api/v1/rooms/', data={
            "name": 'Test room',
            "game_start": timezone.now(),
            "level": 1,
            "map": 1,
            "players_number": 8,
            "searched_players_number": 7,
            "comment": "hej",
        }, format='json')
        rooms_after = Room.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(rooms_after, rooms_before + 1)
        host_id = response.json().get('host')
        self.assertEqual(response.json().get('participants')[0].get('id'), self.user.id)
        self.assertEqual(host_id, self.user.id)

    def test_join_room(self):
        before = self.room.participants.count()
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        after = self.room.participants.count()
        self.assertEqual(after, before + 1)
        self.assertIn(self.user, self.room.participants.all())

    def test_already_joined(self):
        self.assertEqual(self.room.participants.count(), 0)
        self.room.participants.add(self.user)
        self.assertEqual(self.room.participants.count(), 1)
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.room.participants.count(), 1)
        self.assertIn(self.user, self.room.participants.all())

    def test_leave_room(self):
        self.room.participants.add(self.user)
        before = self.room.participants.count()
        response = self.client.delete(
            f'/api/v1/rooms/{self.room.id}/leave/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user, self.room.participants.all())
        # self.room.refresh_from_db() --> gdy zapomina sprawdzić stan bazy
        after = self.room.participants.count()
        self.assertEqual(after, before - 1)

    def test_leave_room_not_participant(self):
        before = self.room.participants.count()
        response = self.client.delete(
            f'/api/v1/rooms/{self.room.id}/leave/',
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn(self.user, self.room.participants.all())
        after = self.room.participants.count()
        self.assertEqual(after, before)

    def test_remove_user_by_host(self):
        user = UserFactory()
        self.room.host = self.user  # czynię dodawanego usera hostem, żeby był on hostem
        self.room.save()  # zapisuję hosta
        self.room.participants.add(user)
        self.room.participants.add(self.room.host)
        response = self.client.delete(
            f'/api/v1/rooms/{self.room.id}/remove_participant/',
            data={
                'user_id': user.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)

    def test_remove_user_by_host_user_not_participant(self):
        user = UserFactory()
        self.room.host = self.user
        self.room.save()
        response = self.client.delete(
            f'/api/v1/rooms/{self.room.id}/remove_participant/',
            data={
                'user_id': user.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_remove_user_by_host_not_host(self):
        user = UserFactory()
        user_the_real_host = UserFactory()
        self.room.host = user_the_real_host
        self.room.save()
        self.room.participants.add(user)
        response = self.client.delete(
            f'/api/v1/rooms/{self.room.id}/remove_participant/',
            data={
                'user_id': user.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_report_user_mail_admins(self):
        user_reported = UserFactory()
        comment = 'They cheated!'
        url = f'/api/v1/rooms/{self.room.id}/report_user/'
        with patch('among_us_finder_rest.apps.room.views.send_mail_to_admins') as mock:
            response = self.client.post(
                url,
                data={
                    'reported_user_id': user_reported.id,
                    'comment': comment,
                },
                format='json',
            )
            self.assertEqual(response.status_code, 200)
            mock.assert_called_once_with(f'User {self.user.id} reported user {user_reported.id} because {comment}')


class MessageTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.room = RoomFactory()

    def setUp(self):
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_message(self):
        self.room.participants.add(self.user)
        messages_before = Message.objects.count()
        response = self.client.post('/api/v1/message/', data={
            "comment": "turururur",
            "room": self.room.id,
        }, format='json')
        messages_after = Message.objects.count()
        # print(response.json()) --> gdy nie wiem co za błąd
        self.assertEqual(response.status_code, 201)
        self.assertEqual(messages_after, messages_before + 1)
        author_id = response.json().get('author')
        room_id = response.json().get('room')
        self.assertEqual(author_id, self.user.id)
        self.assertEqual(room_id, self.room.id)

    def test_create_message_not_participant(self):
        messages_before = Message.objects.count()
        response = self.client.post('/api/v1/message/', data={
            "comment": "turururur",
            "room": self.room.id,
        }, format='json')
        messages_after = Message.objects.count()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(messages_after, messages_before)
        self.assertEqual(response.json().get('author'), ['Nie możesz napisać komentarza w pokoju, w którym nie jesteś'])

    def test_create_message_empty(self):
        self.room.participants.add(self.user)
        messages_before = Message.objects.count()
        response = self.client.post('/api/v1/message/', data={
            "comment": "",
            "room": self.room.id,
        }, format='json')
        messages_after = Message.objects.count()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(messages_after, messages_before)
