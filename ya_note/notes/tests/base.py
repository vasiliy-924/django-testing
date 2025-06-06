from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTE_SLUG = 'test-note'

NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_SUCCESS_URL = reverse('notes:success')
NOTES_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
NOTES_DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))
NOTES_DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
NOTES_HOME_URL = reverse('notes:home')
USERS_LOGIN_URL = reverse('users:login')
USERS_SIGNUP_URL = reverse('users:signup')

NOTES_LIST_REDIRECT = f'{USERS_LOGIN_URL}?next={NOTES_LIST_URL}'
NOTES_ADD_REDIRECT = f'{USERS_LOGIN_URL}?next={NOTES_ADD_URL}'
NOTES_SUCCESS_REDIRECT = f'{USERS_LOGIN_URL}?next={NOTES_SUCCESS_URL}'
NOTES_EDIT_REDIRECT = f'{USERS_LOGIN_URL}?next={NOTES_EDIT_URL}'
NOTES_DELETE_REDIRECT = f'{USERS_LOGIN_URL}?next={NOTES_DELETE_URL}'
NOTES_DETAIL_REDIRECT = f'{USERS_LOGIN_URL}?next={NOTES_DETAIL_URL}'


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст тестовой заметки',
            slug=NOTE_SLUG,
            author=cls.author
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'unique-slug',
        }
