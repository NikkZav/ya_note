from django.test import TestCase
from django.conf import settings
from notes.models import Note
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestNotesPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        for i in range(settings.NOTES_COUNT_ON_PAGE + 1):
            Note.objects.create(
                title=f'{i}',
                text='text',
                author=cls.author
            )
        cls.notes_url = reverse('notes:list')

    def test_max_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.notes_url)
        self.assertEqual(
            response.context['object_list'].count(),
            settings.NOTES_COUNT_ON_PAGE
        )

    def test_order_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.notes_url)
        object_list = response.context['note_list']
        all_title = [note.title for note in object_list]
        sorted_title = sorted(all_title, reverse=True)
        self.assertEqual(all_title, sorted_title)
