from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from notes.models import Note
from .urls_for_tests import NOTE_SLUG, OTHER_SLUG

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.user = User.objects.create(username='Тестовый пользователь')

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.other_note = Note.objects.create(
            title='Другая заметка',
            text='Ещё текст',
            slug=OTHER_SLUG,
            author=cls.user
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст',
            'slug': 'unique-slug',
        }
        cls.new_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }
