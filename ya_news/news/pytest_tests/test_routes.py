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


@pytest.mark.parametrize('url, method', [
    (HOME_URL, 'GET'),
    (LOGIN_URL, 'GET'),
    (LOGOUT_URL, 'POST'),
    (SIGNUP_URL, 'GET'),
    (DETAIL_URL, 'GET'),
])
def test_pages_availability(client, url, method):
    """Общая проверка доступности (200 OK) для всех основных страниц."""
    response = client.generic(method, url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('client, url, expected_status', [
    (lazy_fixture('reader_client'), EDIT_URL, HTTPStatus.NOT_FOUND),
    (lazy_fixture('reader_client'), DELETE_URL, HTTPStatus.NOT_FOUND),
    (lazy_fixture('author_client'), EDIT_URL, HTTPStatus.OK),
    (lazy_fixture('author_client'), DELETE_URL, HTTPStatus.OK),
])
def test_comment_edit_delete_availability(client, url, expected_status):
    """
    Проверяем коды доступа к редактированию и удалению комментариев
    для разных типов пользователей.
    """
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url', ['edit_url', 'delete_url'])
def test_redirect_for_anonymous(client, url, request):
    """
    Анонимный пользователь перенаправляется на страницу логина
    c параметром next=<target_url>.
    """
    target = request.getfixturevalue(url)
    login = request.getfixturevalue('login_url')
    expect = f'{login}?next={target}'

    response = client.get(target)
    assertRedirects(response, expect)
