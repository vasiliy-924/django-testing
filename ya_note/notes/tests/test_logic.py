from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .base import BaseTestCase


class TestNoteCreation(BaseTestCase):
    """Тесты на логику создания, редактирования и удаления заметок."""

    def test_anonymous_user_cant_create_note(self):
        """
        Анонимный пользователь не может создать заметку:
        состав таблицы до и после не изменился.
        """
        before = set(
            Note.objects.values_list('title', 'text', 'slug', 'author_id')
        )
        self.client.post(self.NOTES_ADD_URL, data=self.form_data)
        after = set(
            Note.objects.values_list('title', 'text', 'slug', 'author_id')
        )
        self.assertEqual(before, after)

    def test_user_can_create_note(self):
        """
        Авторизованный пользователь создает заметку:
        добавилась ровно одна запись со всеми полями.
        """
        before = set(Note.objects.all())
        response = self.author_client.post(
            self.NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)

        after = set(Note.objects.all())
        new_notes = after - before
        self.assertEqual(len(after - before), 1)

        new_note = new_notes.pop()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_auto_slug_creation(self):
        """
        При отсутствии 'slug' он генерирутеся из 'title',
        и сохраняется корректно вместе с остальными полями.
        """
        self.form_data['slug'] = ''

        before_slugs = set(Note.objects.values_list('slug', flat=True))
        response = self.author_client.post(
            self.NOTES_ADD_URL,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)

        created = Note.objects.exclude(slug__in=before_slugs).get()
        self.assertEqual(created.slug, slugify(self.form_data['title']))
        self.assertEqual(created.title, self.form_data['title'])
        self.assertEqual(created.text, self.form_data['text'])
        self.assertEqual(created.author, self.author)

    def test_duplicate_slug_validation(self):
        """
        При попытке создать заметку с уже существующим 'slug'
        форма возвращает предупреждение, а в БД не создается новая запись.
        """
        self.form_data['slug'] = self.NOTE_SLUG
        before_slugs = set(Note.objects.values_list('slug', flat=True))

        response = self.author_client.post(
            self.NOTES_ADD_URL,
            data=self.form_data
        )
        self.assertContains(
            response,
            f"{self.form_data['slug']}{WARNING}",
            status_code=HTTPStatus.OK,
        )
        after_slugs = set(Note.objects.values_list('slug', flat=True))
        self.assertEqual(before_slugs, after_slugs)

    def test_author_can_edit_note(self):
        """
        Автор заметки может ее редактировать -
        все поля изменились согласно переданным данным.
        """
        original_author = self.note.author
        response = self.author_client.post(
            self.NOTES_EDIT_URL,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)

        updated = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated.title, self.form_data['title'])
        self.assertEqual(updated.text, self.form_data['text'])
        self.assertEqual(updated.slug, self.form_data['slug'])
        self.assertEqual(updated.author, original_author)

    def test_other_user_cant_edit_note(self):
        """
        Другой пользователь не может редактировать чужую заметку -
        ответ 404 и заметка осталась без изменений.
        """
        response = self.reader_client.post(
            self.NOTES_EDIT_URL,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertEqual(self.note.title, 'Тестовая заметка')
        self.assertEqual(self.note.text, 'Текст')
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        """
        Автор может удалить заметку -
        одна запись удалена, и это именно та, что ожидалась.
        """
        note_pk = self.note.pk
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.NOTES_DELETE_URL)
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)

        self.assertEqual(Note.objects.count(), notes_count_before - 1)
        self.assertFalse(Note.objects.filter(pk=note_pk).exists())

    def test_other_user_cant_delete_note(self):
        """
        Другой пользователь не может удалить чужую заметку -
        ответ 404 и состав таблицы не изменился.
        """
        before = sorted(
            Note.objects.values('pk', 'title', 'text', 'author', 'slug'),
            key=lambda x: x['pk']
        )
        response = self.reader_client.post(self.NOTES_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        after = sorted(
            Note.objects.values('pk', 'title', 'text', 'author', 'slug'),
            key=lambda x: x['pk']
        )
        self.assertEqual(before, after)
