from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .base import (
    BaseTestCase,
    NOTES_ADD_URL,
    NOTES_DELETE_URL,
    NOTES_EDIT_URL,
    NOTES_SUCCESS_URL
)


class TestNoteCreation(BaseTestCase):
    """Тесты на логику создания, редактирования и удаления заметок."""

    def test_anonymous_user_cant_create_note(self):
        """
        Анонимный пользователь не может создать заметку:
        состав таблицы до и после не изменился.
        """
        before = set(Note.objects.all())
        self.client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertEqual(before, set(Note.objects.all()))

    def test_user_can_create_note(self):
        """
        Авторизованный пользователь создает заметку:
        добавилась ровно одна запись со всеми полями.
        """
        before = set(Note.objects.all())
        self.assertRedirects(
            self.author_client.post(NOTES_ADD_URL, data=self.form_data),
            NOTES_SUCCESS_URL
        )

        new_notes = set(Note.objects.all()) - before
        self.assertEqual(len(new_notes), 1)

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
            NOTES_ADD_URL,
            data=self.form_data
        )
        self.assertRedirects(response, NOTES_SUCCESS_URL)

        created = Note.objects.exclude(slug__in=before_slugs).get()
        self.assertEqual(created.slug, slugify(self.form_data['title']))
        self.assertEqual(created.title, self.form_data['title'])
        self.assertEqual(created.text, self.form_data['text'])
        self.assertEqual(created.author, self.author)

    def test_duplicate_slug_does_not_create_new_note(self):
        """
        При попытке создать заметку с уже существующим 'slug'
        форма возвращает предупреждение, а в БД не создается новая запись.
        """
        self.form_data['slug'] = Note.objects.first().slug
        before_slugs = set(Note.objects.all())

        response = self.author_client.post(
            NOTES_ADD_URL,
            data=self.form_data
        )
        self.assertContains(
            response,
            f"{self.form_data['slug']}{WARNING}",
            status_code=HTTPStatus.OK,
        )
        self.assertEqual(
            before_slugs,
            set(Note.objects.all())
        )

    def test_author_can_edit_note(self):
        """
        Автор заметки может ее редактировать -
        все поля изменились согласно переданным данным.
        """
        response = self.author_client.post(
            NOTES_EDIT_URL,
            data=self.form_data
        )
        self.assertRedirects(response, NOTES_SUCCESS_URL)

        updated = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated.title, self.form_data['title'])
        self.assertEqual(updated.text, self.form_data['text'])
        self.assertEqual(updated.slug, self.form_data['slug'])
        self.assertEqual(updated.author, self.note.author)

    def test_non_author_cannot_edit_note(self):
        """
        Другой пользователь не может редактировать чужую заметку -
        ответ 404 и заметка осталась без изменений.
        """
        response = self.reader_client.post(
            NOTES_EDIT_URL,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, 'Тестовая заметка')
        self.assertEqual(note.text, 'Текст тестовой заметки')
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_author_can_delete_note(self):
        """
        Автор может удалить заметку -
        одна запись удалена, и это именно та, что ожидалась.
        """
        notes_count_before = Note.objects.count()
        self.assertRedirects(
            self.author_client.post(NOTES_DELETE_URL),
            NOTES_SUCCESS_URL
        )

        self.assertEqual(Note.objects.count(), notes_count_before - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_other_user_cant_delete_note(self):
        """
        Другой пользователь не может удалить чужую заметку -
        ответ 404 и состав таблицы не изменился.
        """
        before = set(Note.objects.all())

        response = self.reader_client.post(NOTES_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertEqual(before, set(Note.objects.all()))
