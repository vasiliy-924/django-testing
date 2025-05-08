from .base import (
    BaseTestCase,
    NOTES_ADD_URL,
    NOTES_EDIT_URL,
    NOTES_LIST_URL
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
        self.assertIn('object_list', response.context)
        obj_list = response.context['object_list']
        self.assertIn(self.note, obj_list)

        note_from_db = obj_list.get(slug=self.NOTE_SLUG)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

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
