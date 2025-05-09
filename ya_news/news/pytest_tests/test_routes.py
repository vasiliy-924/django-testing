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


@pytest.mark.parametrize('url, method', [
    (HOME_URL, 'GET'),
    (LOGIN_URL, 'GET'),
    (LOGOUT_URL, 'POST'),
    (SIGNUP_URL, 'GET'),
    (DETAIL_URL, 'GET'),
])
def test_pages_availability(client, url, method):
    """Доступность основных страниц (200 OK)."""
    assert client.generic(method, url).status_code == HTTPStatus.OK


@pytest.mark.parametrize('client, url, expected_status', [
    (READER_CLIENT, EDIT_URL, HTTPStatus.NOT_FOUND),
    (READER_CLIENT, DELETE_URL, HTTPStatus.NOT_FOUND),
    (AUTHOR_CLIENT, EDIT_URL, HTTPStatus.OK),
    (AUTHOR_CLIENT, DELETE_URL, HTTPStatus.OK),
])
def test_comment_edit_delete_availability(client, url, expected_status):
    """Коды доступа к редактированию и удалению комментариев."""
    assert client.get(url).status_code == expected_status


@pytest.mark.parametrize('url, expected_redirect', [
    (EDIT_URL, EDIT_LOGIN_REDIRECT),
    (DELETE_URL, DELETE_LOGIN_REDIRECT),
])
def test_redirect_for_anonymous(client, url, expected_redirect):
    """Аноним (GET) → перенаправление на логин с next."""
    assertRedirects(
        client.get(url),
        expected_redirect,
        status_code=HTTPStatus.FOUND,
    )
