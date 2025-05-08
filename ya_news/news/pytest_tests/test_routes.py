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


def test_pages_availability(
    client,
    home_url, login_url, logout_url,
    signup_url, detail_url
):
    """Общая проверка доступности (200 OK) для всех основных страниц."""
    urls_and_methods = [
        (home_url, 'GET'),
        (login_url, 'GET'),
        (logout_url, 'POST'),
        (signup_url, 'GET'),
        (detail_url, 'GET'),
    ]
    for url, method in urls_and_methods:
        response = client.generic(method, url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('client, url, expected_status', [
    (READER_CLIENT, EDIT_URL, HTTPStatus.NOT_FOUND),
    (READER_CLIENT, DELETE_URL, HTTPStatus.NOT_FOUND),
    (AUTHOR_CLIENT, EDIT_URL, HTTPStatus.OK),
    (AUTHOR_CLIENT, DELETE_URL, HTTPStatus.OK),
])
def test_comment_edit_delete_availability(client, url, expected_status):
    """
    Проверяем доступ к редактированию и удалению комментариев
    для reader и author клиентов.
    """
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('target_url, expected_redirect', [
    (EDIT_URL, EDIT_LOGIN_REDIRECT),
    (DELETE_URL, DELETE_LOGIN_REDIRECT),
])
def test_redirect_for_anonymous(client, target_url, expected_redirect):
    """
    Анонимный пользователь перенаправляется на страницу логина
    c параметром next=<target_url>.
    """
    assertRedirects(client.get(target_url), expected_redirect, status_code=HTTPStatus.FOUND)
