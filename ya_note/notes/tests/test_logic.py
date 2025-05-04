# test_logic.py
from pytils.translit import slugify
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Тестовый пользователь')
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст',
            'slug': 'test-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_user_can_create_note(self):
        self.client.force_login(self.user)
        notes_count_before = Note.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)

    def test_auto_slug_creation(self):
        self.client.force_login(self.user)
        form_data = {
            'title': 'Новая заметка без slug',
            'text': 'Текст',
            'slug': ''
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get(title=form_data['title'])
        expected_slug = slugify(form_data['title'])[:100]
        self.assertEqual(new_note.slug, expected_slug)

    def test_duplicate_slug_validation(self):
        Note.objects.create(
            title='Тест',
            text='Текст',
            slug='test-slug',
            author=self.user
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)
        self.assertContains(
            response,
            f'test-slug{WARNING}',
            status_code=HTTPStatus.OK
        )
        self.assertEqual(Note.objects.filter(slug='test-slug').count(), 1)


class TestNoteEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-note',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.new_data = {  # Исправлено с self на cls
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.edit_url,
            data=self.new_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_data['title'])

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(
            self.edit_url,
            data=self.new_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_other_user_cant_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
