from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый текст'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author, author_client, news, detail_url):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    assert Comment.objects.count() == 1

    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    """Комментарий с запрещённым словом не проходит валидацию."""
    data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(detail_url, data=data)
    form = response.context['form']
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, delete_url, detail_url):
    """Автор комментария может удалить свой комментарий."""
    initial_count = Comment.objects.count()
    response = author_client.delete(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url + '#comments'
    assert Comment.objects.count() == initial_count - 1


def test_reader_cant_delete_comment(reader_client, delete_url):
    """Чужой пользователь не может удалить комментарий."""
    initial_count = Comment.objects.count()
    response = reader_client.delete(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count


def test_author_can_edit_comment(author_client, edit_url, detail_url, comment):
    """Автор комментария может его отредактировать."""
    initial_author = comment.author
    initial_news = comment.news
    response = author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url + '#comments'

    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == initial_author
    assert updated_comment.news == initial_news


def test_reader_cant_edit_comment(reader_client, edit_url, comment):
    """Чужой пользователь не может отредактировать комментарий."""
    initial_text = comment.text
    initial_author = comment.author
    initial_news = comment.news
    response = reader_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND

    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == initial_text
    assert unchanged_comment.author == initial_author
    assert unchanged_comment.news == initial_news
