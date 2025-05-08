from .base import (
    BaseTestCase,
    NOTE_SLUG,
    NOTES_ADD_URL,
    NOTES_EDIT_URL,
    NOTES_LIST_URL,
)
from notes.forms import NoteForm


class TestContent(BaseTestCase):
    """
    Тесты для основных страниц приложения заметок:
    список, создание и редактирование.
    """

    def test_notes_list_for_author(self):
        """Автор должен видеть свою заметку в списке со всеми полями."""
        response = self.author_client.get(NOTES_LIST_URL)
        obj_list = response.context['object_list']

        note = self.note
        self.assertIn(note, obj_list)
        self.assertEqual(note.title, 'Тестовая заметка')
        self.assertEqual(note.text, 'Текст тестовой заметки')
        self.assertEqual(note.slug, NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_notes_list_for_other_user(self):
        """
        Другой пользователь не должен видеть
        чужую заметку в общем списке.
        """
        self.assertNotIn(
            self.note,
            self.reader_client.get(NOTES_LIST_URL).context['object_list']
        )

    def test_create_and_edit_pages_contain_form(self):
        """
        Страницы создания и редактирования должны возвращать
        корректную форму NoteForm.
        """
        for url in (NOTES_ADD_URL, NOTES_EDIT_URL):
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.author_client.get(url).context.get('form'),
                    NoteForm
                )
