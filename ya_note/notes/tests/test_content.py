from .base import (
    BaseTestCase,
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
        notes = response.context['object_list']

        note = notes.filter(id=self.note.id).first()
        self.assertIn(self.note, notes)
        self.assertIsNotNone(
            note,
            f"Заметка с id {self.note.id} не найдена в списке заметок."
        )

        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

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
