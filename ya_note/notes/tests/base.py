from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    NOTE_SLUG = 'test-note'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст',
            'slug': 'unique-slug',
        }

        cls.NOTES_LIST_URL = reverse('notes:list')
        cls.NOTES_ADD_URL = reverse('notes:add')
        cls.NOTES_SUCCESS_URL = reverse('notes:success')
        cls.NOTES_EDIT_URL = reverse('notes:edit', args=(cls.NOTE_SLUG,))
        cls.NOTES_DELETE_URL = reverse('notes:delete', args=(cls.NOTE_SLUG,))
        cls.NOTES_DETAIL_URL = reverse('notes:detail', args=(cls.NOTE_SLUG,))

    @classmethod
    def get_expected_redirect(cls, url):
        """Возвращает URL перенаправления на логин с параметром next."""
        login_url = reverse('users:login')
        return f'{login_url}?next={url}'
