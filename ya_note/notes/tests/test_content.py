from .base import BaseTestCase
from .urls_for_tests import NOTES_LIST_URL, NOTES_ADD_URL, OTHER_EDIT_URL
from notes.forms import NoteForm


class TestContent(BaseTestCase):
    """
    Тесты для основных страниц приложения заметок:
    список, создание и редактирование.
    """

    def test_notes_list_for_author(self):
        """
        Автор должен видеть свою заметку в списке со всеми полями.
        """
        response = self.author_client.get(NOTES_LIST_URL)
        self.assertIn('object_list', response.context)
        obj_list = response.context['object_list']
        self.assertIn(self.note, obj_list)

        note_ctx = next(n for n in obj_list if n.slug == self.note.slug)
        self.assertEqual(note_ctx.title, self.note.title)
        self.assertEqual(note_ctx.text, self.note.text)
        self.assertEqual(note_ctx.slug, self.note.slug)
        self.assertEqual(note_ctx.author, self.note.author)

    def test_notes_list_for_other_user(self):
        """Другой пользователь не должен видеть чужую заметку в общем списке."""
        response = self.reader_client.get(NOTES_LIST_URL)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_create_and_edit_pages_contain_form(self):
        """
        Страницы создания и редактирования должны возвращать
        корректную форму NoteForm.
        """
        for url in (NOTES_ADD_URL, OTHER_EDIT_URL):
            response = self.user_client.get(url)
            form = response.context.get('form')
            self.assertIsInstance(form, NoteForm)
