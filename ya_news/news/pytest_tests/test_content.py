import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from news.forms import CommentForm


User = get_user_model()

pytestmark = pytest.mark.django_db


def test_news_count(client, news_items, home_url):
    """
    Главная страница должна показывать ровно
    NEWS_COUNT_ON_HOME_PAGE новостей.
    """
    assert len(client.get(home_url).context['object_list']
               ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_items, home_url):
    """Новости на главной должны быть в порядке убывания даты."""
    dates = [news.date for news in client.get(home_url).context['object_list']]
    assert dates == sorted(dates, reverse=True)


def test_comments_order(client, comments_for_news, detail_url):
    """
    На странице детали комментарии должны идти
    по возрастанию времени создания.
    """
    response = client.get(detail_url)
    timestamps = [
        c.created for c in response.context['news'].comment_set.all()]
    assert timestamps == sorted(timestamps)


def test_comment_form_for_anonymous(client, detail_url):
    """Анонимный пользователь не видит форму комментария."""
    assert client.get(detail_url).context.get('form') is None


def test_comment_form_for_author_user(author_client, detail_url):
    """Авторизованный пользователь видит форму комментария нужного типа."""
    assert isinstance(
        author_client.get(detail_url).context.get('form'),
        CommentForm
    )
