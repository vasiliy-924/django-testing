from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db

HOME_URL = lazy_fixture('home_url')
LOGIN_URL = lazy_fixture('login_url')
LOGOUT_URL = lazy_fixture('logout_url')
SIGNUP_URL = lazy_fixture('signup_url')
DETAIL_URL = lazy_fixture('detail_url')
EDIT_URL = lazy_fixture('edit_url')
DELETE_URL = lazy_fixture('delete_url')
EDIT_LOGIN_REDIRECT = lazy_fixture('edit_login_redirect')
DELETE_LOGIN_REDIRECT = lazy_fixture('delete_login_redirect')

READER_CLIENT = lazy_fixture('reader_client')
AUTHOR_CLIENT = lazy_fixture('author_client')
ANON_CLIENT = lazy_fixture('client')


@pytest.mark.parametrize('user_client, url, method, expected_status', [
    # Основные страницы
    (ANON_CLIENT, HOME_URL, 'GET', HTTPStatus.OK),
    (ANON_CLIENT, LOGIN_URL, 'GET', HTTPStatus.OK),
    (ANON_CLIENT, LOGOUT_URL, 'POST', HTTPStatus.OK),
    (ANON_CLIENT, SIGNUP_URL, 'GET', HTTPStatus.OK),
    (ANON_CLIENT, DETAIL_URL, 'GET', HTTPStatus.OK),
    # Редактирование и удаление комментариев для разных ролей
    (READER_CLIENT, EDIT_URL, 'GET', HTTPStatus.NOT_FOUND),
    (READER_CLIENT, DELETE_URL, 'GET', HTTPStatus.NOT_FOUND),
    (AUTHOR_CLIENT, EDIT_URL, 'GET', HTTPStatus.OK),
    (AUTHOR_CLIENT, DELETE_URL, 'GET', HTTPStatus.OK),
    # Перенаправления для анонимных пользователей
    (ANON_CLIENT, EDIT_URL, 'GET', HTTPStatus.FOUND),
    (ANON_CLIENT, DELETE_URL, 'GET', HTTPStatus.FOUND),
])
def test_status_codes(user_client, url, method, expected_status):
    """
    Проверка кодов ответов: доступность страниц,
    комментирование и перенаправления.
    """
    response = user_client.generic(method, url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url, expected_redirect', [
    (EDIT_URL, EDIT_LOGIN_REDIRECT),
    (DELETE_URL, DELETE_LOGIN_REDIRECT),
])
def test_redirect_for_anonymous(client, url, expected_redirect):
    """Аноним (GET) → перенаправление на логин с next."""
    assertRedirects(
        client.get(url),
        expected_redirect
    )
