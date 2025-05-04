# test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesList(TestCase):
    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            slug='test-note',
            author=cls.author
        )

    def test_notes_list_for_author(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_notes_list_for_other_user(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.NOTES_LIST_URL)
        self.assertNotIn(self.note, response.context['object_list'])


class TestNoteCreationAndEditPages(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Тестовый пользователь')
        cls.add_url = reverse('notes:add')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='test-slug',
            author=cls.user
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_create_page_contains_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.add_url)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url)
        self.assertIsInstance(response.context['form'], NoteForm)
