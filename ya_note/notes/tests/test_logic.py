from http import HTTPStatus
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .base import BaseTestCase
from .urls_for_tests import (
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
        before = list(
            Note.objects.values_list('title', 'text', 'slug', 'author_id')
        )
        self.client.post(NOTES_ADD_URL, data=self.form_data)
        after = list(
            Note.objects.values_list('title', 'text', 'slug', 'author_id')
        )
        self.assertEqual(before, after)

    def test_user_can_create_note(self):
        """
        Авторизованный пользователь создает заметку:
        добавилась ровно одна запись со всеми полями.
        """
        before = list(
            Note.objects.values_list('title', 'text', 'slug', 'author_id')
        )
        response = self.user_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)

        after = list(
            Note.objects.values_list('title', 'text', 'slug', 'author_id')
        )
        self.assertEqual(len(before) + 1, len(after))

        new = [item for item in after if item not in before]
        self.assertEqual(len(new), 1)
        title, text, slug, author_id = new[0]
        self.assertEqual(title, self.form_data['title'])
        self.assertEqual(text, self.form_data['text'])
        self.assertEqual(slug, self.form_data['slug'])
        self.assertEqual(author_id, self.user.id)

    def test_auto_slug_creation(self):
        """
        При отсутствии 'slug' он генерирутеся из 'title',
        и сохраняется корректно вместе с остальными полями.
        """
        form_data = self.form_data.copy()
        form_data['slug'] = ''

        before_slugs = set(Note.objects.values_list('slug', flat=True))
        response = self.user_client.post(NOTES_ADD_URL, data=form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)

        created = Note.objects.exclude(slug__in=before_slugs).get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(created.slug, expected_slug)
        self.assertEqual(created.title, form_data['title'])
        self.assertEqual(created.text, form_data['text'])
        self.assertEqual(created.author_id, self.user.id)  # <-------- check

    def test_duplicate_slug_validation(self):
        """
        При попытке создать заметку с уже существующим 'slug'
        форма возвращает предупреждение, а в БД не создается новая запись.
        """
        Note.objects.create(
            title='Тест',
            text='Текст',
            slug=self.form_data['slug'],
            author=self.user
        )
        before_slugs = list(Note.objects.values_list('slug', flat=True))

        response = self.user_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertContains(
            response,
            f"{self.form_data['slug']}{WARNING}",
            status_code=HTTPStatus.OK,
        )
        after_slugs = list(Note.objects.values_list('slug', flat=True))
        self.assertEqual(before_slugs, after_slugs)

    # failed
    def test_author_can_edit_note(self):
        """
        Автор заметки может ее редактировать -
        все поля изменились согласно переданным данным.
        """
        response = self.author_client.post(NOTES_EDIT_URL, data=self.new_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)

        updated = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated.title, self.new_data['title'])
        self.assertEqual(updated.text, self.new_data['text'])
        self.assertEqual(updated.slug, self.new_data['slug'])
        self.assertEqual(updated.author_id, self.author.id)

    def test_other_user_cant_edit_note(self):
        """
        Другой пользователь не может редактировать чужую заметку -
        ответ 404 и заметка осталась без изменений.
        """
        before = Note.objects.values_list(
            'title', 'text', 'slug', 'author_id'
        ).get(pk=self.note.pk)
        response = self.reader_client.post(NOTES_EDIT_URL, data=self.new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        after = Note.objects.values_list(
            'title', 'text', 'slug', 'author_id'
        ).get(pk=self.note.pk)
        self.assertEqual(before, after)

    # failed
    def test_author_can_delete_note(self):
        """
        Автор может удалить заметку -
        одна запись удалена, и это именно та, что ожидалась.
        """
        before = set(Note.objects.values_list('pk', flat=True))
        response = self.author_client.post(NOTES_DELETE_URL)
        self.assertRedirects(response, NOTES_SUCCESS_URL)

        after = set(Note.objects.values_list('pk', flat=True))
        removed = before - after
        self.assertEqual(len(removed), 1)
        self.assertEqual({self.note.pk}, removed)

    def test_other_user_cant_delete_note(self):
        """
        Другой пользователь не может удалить чужую заметку -
        ответ 404 и состав таблицы не изменился.
        """
        before = set(Note.objects.values_list('pk'))
        response = self.reader_client.post(NOTES_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        after = set(Note.objects.values_list('pk'))
        self.assertEqual(before, after)
