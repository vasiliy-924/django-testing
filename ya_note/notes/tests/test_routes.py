from http import HTTPStatus

from .base import (
    BaseTestCase,
    NOTES_ADD_REDIRECT,
    NOTES_ADD_URL,
    NOTES_DELETE_REDIRECT,
    NOTES_DELETE_URL,
    NOTES_DETAIL_REDIRECT,
    NOTES_DETAIL_URL,
    NOTES_EDIT_REDIRECT,
    NOTES_EDIT_URL,
    NOTES_HOME_URL,
    NOTES_LIST_REDIRECT,
    NOTES_LIST_URL,
    NOTES_SUCCESS_REDIRECT,
    NOTES_SUCCESS_URL,
    USERS_LOGIN_URL,
    USERS_SIGNUP_URL,
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
            (NOTES_HOME_URL, self.client, HTTPStatus.OK),
            (USERS_LOGIN_URL, self.client, HTTPStatus.OK),
            (USERS_SIGNUP_URL, self.client, HTTPStatus.OK),

            # защищённые для автора
            (NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            (NOTES_ADD_URL, self.author_client, HTTPStatus.OK),
            (NOTES_SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (NOTES_EDIT_URL, self.author_client, HTTPStatus.OK),
            (NOTES_DELETE_URL, self.author_client, HTTPStatus.OK),
            (NOTES_DETAIL_URL, self.author_client, HTTPStatus.OK),

            # чужие для reader
            (NOTES_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTES_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTES_DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND),

            # защищённые для анонимного
            (NOTES_LIST_URL, self.client, HTTPStatus.FOUND),
            (NOTES_ADD_URL, self.client, HTTPStatus.FOUND),
            (NOTES_SUCCESS_URL, self.client, HTTPStatus.FOUND),
            (NOTES_EDIT_URL, self.client, HTTPStatus.FOUND),
            (NOTES_DELETE_URL, self.client, HTTPStatus.FOUND),
            (NOTES_DETAIL_URL, self.client, HTTPStatus.FOUND),
        ]

        for url, client, expected in cases:
            with self.subTest(url=url, client=client, expected=expected):
                self.assertEqual(client.get(url).status_code, expected)

    def test_login_redirects(self):
        """
        Контроль перенаправлений анонимного пользователя
        на страницу логина с параметром next.
        """
        redirect_cases = [
            (NOTES_LIST_URL, NOTES_LIST_REDIRECT),
            (NOTES_ADD_URL, NOTES_ADD_REDIRECT),
            (NOTES_SUCCESS_URL, NOTES_SUCCESS_REDIRECT),
            (NOTES_EDIT_URL, NOTES_EDIT_REDIRECT),
            (NOTES_DELETE_URL, NOTES_DELETE_REDIRECT),
            (NOTES_DETAIL_URL, NOTES_DETAIL_REDIRECT),
        ]

        for url, expected_redirect in redirect_cases:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
