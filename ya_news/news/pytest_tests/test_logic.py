# test_logic.py
import pytest

from http import HTTPStatus
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news_id, form_data):
    url = reverse('news:detail', args=news_id)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, author, news, news_id, form_data
):
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, news_id):
    url = reverse('news:detail', args=news_id)
    data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=data)
    form = response.context['form']
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    "client_fixture, expected_status, expect_redirect",
    [
        ('author_client', HTTPStatus.FOUND, True),
        ('reader_client', HTTPStatus.NOT_FOUND, False),
    ]
)
def test_delete_comment(
    client_fixture, request, comment, news_id, expect_redirect, expected_status
):
    client = request.getfixturevalue(client_fixture)
    detail_url = reverse('news:detail', args=news_id) + '#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    response = client.delete(delete_url)
    assert response.status_code == expected_status
    if expect_redirect:
        assert response.url == detail_url
    assert Comment.objects.count() == (0 if expect_redirect else 1)


@pytest.mark.parametrize(
    "client_fixture, expected_status, expected_text",
    [
        ('author_client', HTTPStatus.FOUND, 'Новый текст'),
        ('reader_client', HTTPStatus.NOT_FOUND, 'Текст комментария'),
    ]
)
def test_edit_comment(
    client_fixture, request, comment, news_id,
    form_data, expected_status, expected_text
):
    client = request.getfixturevalue(client_fixture)
    detail_url = reverse('news:detail', args=news_id) + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    response = client.post(edit_url, data=form_data)
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        assert response.url == detail_url
    comment.refresh_from_db()
    assert comment.text == expected_text
