from .base import (
    BaseTestCase,
    NOTES_ADD_URL,
    NOTES_EDIT_URL,
    NOTES_DETAIL_URL,
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
        self.assertIn(self.note, response.context['object_list'])
        self.assertContains(response, f"{self.note.id}:")
        self.assertContains(response, self.note.title)
        detail_url = NOTES_DETAIL_URL
        self.assertContains(response, f'href="{detail_url}"')

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
