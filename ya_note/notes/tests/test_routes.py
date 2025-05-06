from http import HTTPStatus

from django.urls import reverse

from .base import BaseTestCase
from .urls_for_tests import (
    NOTES_ADD_URL,
    NOTES_DELETE_URL,
    NOTES_EDIT_URL,
    NOTES_SUCCESS_URL,
    NOTES_LIST_URL
)


class TestRoutes(BaseTestCase):
    """Проверка доступности маршрутов и редиректов в приложении notes."""

    def test_status_codes(self):
        """
        Контроль всех кодов возврата для разных комбинаций урл + клиент:
        - публичные страницы для анонимов,
        - защищённые страницы для авторизованных,
        - недоступные страницы для чужих пользователей.
        """
        cases = [
            # публичные для анонимного
            (reverse('notes:home'), self.client, HTTPStatus.OK),
            (reverse('users:login'), self.client, HTTPStatus.OK),
            (reverse('users:signup'), self.client, HTTPStatus.OK),

            # защищённые для автора
            (NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            (NOTES_ADD_URL, self.author_client, HTTPStatus.OK),
            (NOTES_SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (NOTES_EDIT_URL, self.author_client, HTTPStatus.OK),
            (NOTES_DELETE_URL, self.author_client, HTTPStatus.OK),

            # чужие для reader
            (NOTES_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTES_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),

            # защищённые для анонимного
            (NOTES_LIST_URL, self.client, HTTPStatus.FOUND),
            (NOTES_ADD_URL, self.client, HTTPStatus.FOUND),
            (NOTES_SUCCESS_URL, self.client, HTTPStatus.FOUND),
        ]

        for url, client, expected in cases:
            with self.subTest(url=url, client=client, expected=expected):
                self.assertEqual(client.get(url).status_code, expected)

    def test_login_redirects(self):
        """
        Контроль перенаправлений анонимного пользователя
        на страницу логина с параметром next.
        """
        login_url = reverse('users:login')
        protected = [
            NOTES_LIST_URL,
            NOTES_ADD_URL,
            NOTES_SUCCESS_URL,
            NOTES_EDIT_URL,
            NOTES_DELETE_URL,
        ]

        for url in protected:
            with self.subTest(url=url):
                expected = f'{login_url}?next={url}'
                self.assertRedirects(self.client.get(url), expected)
