# test_routes.py
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', lazy_fixture('news_id')),
    ]
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client, expected_status',
    [
        (lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK),
    ]
)
@pytest.mark.parametrize(
    'view_name',
    ['news:edit', 'news:delete']
)
def test_comment_edit_delete_availability(
    client, view_name, comment, expected_status
):
    url = reverse(view_name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'view_name',
    ['news:edit', 'news:delete']
)
def test_redirect_for_anonymous(client, view_name, comment):
    login_url = reverse('users:login')
    target = reverse(view_name, args=(comment.id,))
    expect = f'{login_url}?next={target}'
    response = client.get(target)
    assertRedirects(response, expect)
