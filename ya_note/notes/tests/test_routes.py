from http import HTTPStatus

from django.urls import reverse


from .base import BaseTestCase


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
            (self.NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_ADD_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_EDIT_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_DELETE_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_DETAIL_URL, self.author_client, HTTPStatus.OK),

            # чужие для reader
            (self.NOTES_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.NOTES_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.NOTES_DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND),

            # защищённые для анонимного
            (self.NOTES_LIST_URL, self.client, HTTPStatus.FOUND),
            (self.NOTES_ADD_URL, self.client, HTTPStatus.FOUND),
            (self.NOTES_SUCCESS_URL, self.client, HTTPStatus.FOUND),
            (self.NOTES_DETAIL_URL, self.client, HTTPStatus.FOUND),
        ]

        for url, client, expected in cases:
            with self.subTest(url=url, client=client, expected=expected):
                self.assertEqual(client.get(url).status_code, expected)

    def test_login_redirects(self):
        """
        Контроль перенаправлений анонимного пользователя
        на страницу логина с параметром next.
        """
        protected = [
            self.NOTES_LIST_URL,
            self.NOTES_ADD_URL,
            self.NOTES_SUCCESS_URL,
            self.NOTES_EDIT_URL,
            self.NOTES_DELETE_URL,
            self.NOTES_DETAIL_URL,
        ]

        for url in protected:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    self.get_expected_redirect(url)
                )
