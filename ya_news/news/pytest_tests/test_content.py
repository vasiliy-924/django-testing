# test_content.py
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from pytest_lazyfixture import lazy_fixture

from news.models import News, Comment
from news.forms import CommentForm

User = get_user_model()


@pytest.fixture
@pytest.mark.django_db
def home_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {i}',
            text='Просто текст.',
            date=today - timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.mark.django_db
def test_news_count(home_news, client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(home_news, client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.fixture
@pytest.mark.django_db
def detail_data():
    news = News.objects.create(
        title='Тестовая новость',
        text='Просто текст'
    )
    author = User.objects.create(username='Комментатор')
    now = timezone.now()
    for idx in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {idx}'
        )
        comment.created = now + timedelta(days=idx)
        comment.save()
    detail_url = reverse('news:detail', args=(news.id,))
    return {'url': detail_url}


@pytest.mark.django_db
def test_comments_order(detail_data, client):
    response = client.get(detail_data['url'])
    news_obj = response.context['news']
    timestamps = [c.created for c in news_obj.comment_set.all()]
    assert timestamps == sorted(timestamps)


@pytest.mark.parametrize(
    'client_fixture, expected',
    [
        (lazy_fixture('client'), False),
        (lazy_fixture('author_client'), True),
    ]
)
@pytest.mark.django_db
def test_comment_form_presence(detail_data, client_fixture, expected):
    response = client_fixture.get(detail_data['url'])
    has_form = 'form' in response.context
    assert has_form == expected
    if expected:
        assert isinstance(response.context['form'], CommentForm)
