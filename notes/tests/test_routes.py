from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from django.contrib.auth import get_user_model

from notes.models import Note
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='author of note'
        )
        cls.note = Note.objects.create(
            text='Abrakadabra',
            author=cls.author
        )
        cls.reader = User.objects.create(
            username='reader'
        )

    def test_pages_availability_everybody(self):
        urls = (
            ('notes:home', HTTPStatus.OK),
            ('users:login', HTTPStatus.OK),
            ('users:signup', HTTPStatus.OK)
        )

        for name_url, status in urls:
            with self.subTest(name_url=name_url):
                url = reverse(name_url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_pages_availability_registered_and_guest(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        users_status = (
            ('guest', None),
            ('registered', HTTPStatus.OK)
        )

        login_url = reverse('users:login')

        for user, status in users_status:
            if user == 'registered':
                self.client.force_login(self.author)
            else:
                self.client.logout()
            
            for name_url, args in urls:
                with self.subTest(name_url=name_url,
                                  user=user,
                                  status=status):
                    url = reverse(name_url, args=args)
                    response = self.client.get(url)
                    if user == 'guest':
                        self.assertRedirects(response, f'{login_url}?next={url}')
                    else:
                        self.assertEqual(response.status_code, status)

    def test_pages_availability_reader_and_author(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        urls_status = (
            (self.reader, HTTPStatus.NOT_FOUND),
            (self.author, HTTPStatus.OK),
        )

        for user, status in urls_status:
            for name_url, args in urls:
                self.client.force_login(user)
                with self.subTest(name_url=name_url,
                                  user=user
                                  ):
                    url = reverse(name_url, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

