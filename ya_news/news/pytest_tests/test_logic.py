from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый текст'}
BAD_WORD_TEXT = 'Какой-то текст, {}, еще текст'


def test_anonymous_user_cant_create_comment(client, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    assert client.post(
        detail_url,
        data=FORM_DATA
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author, author_client, news,
    detail_url, detail_url_with_comments
):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments
    assert Comment.objects.count() == 1

    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    """Комментарий с запрещённым словом не проходит валидацию."""
    data = {'text': BAD_WORD_TEXT.format(bad_word)}
    response = author_client.post(detail_url, data=data)
    form = response.context['form']
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client, delete_url, detail_url_with_comments, comment
):
    """Автор комментария может удалить свой комментарий."""
    before_ids = set(Comment.objects.values_list('id', flat=True))

    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments

    after_ids = set(Comment.objects.values_list('id', flat=True))
    assert comment.id in before_ids
    assert comment.id not in after_ids
    assert after_ids == (before_ids - {comment.id})


def test_reader_cant_delete_comment(reader_client, delete_url):
    """Чужой пользователь не может удалить комментарий."""
    before_ids = set(Comment.objects.values_list('id', flat=True))

    response = reader_client.delete(delete_url)
    after_ids = set(Comment.objects.values_list('id', flat=True))

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert before_ids == after_ids


def test_author_can_edit_comment(
    author_client, edit_url, detail_url_with_comments, comment
):
    """Автор комментария может его отредактировать."""
    response = author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_with_comments

    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_reader_cant_edit_comment(reader_client, edit_url, comment):
    """Чужой пользователь не может отредактировать комментарий."""
    response = reader_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND

    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.author == comment.author
    assert unchanged_comment.news == comment.news
