# conftest.py
from datetime import timedelta
import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.test.client import Client

from news.models import News, Comment


User = get_user_model()

pytestmark = pytest.mark.django_db

# ----------------------------------------------------------------
@pytest.fixture
def author():
    """Пользователь-автор комментариев."""
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
def reader():
    return User.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client
# ----------------------------------------------------------------------


@pytest.fixture
def news():
    """Одна тестовая новость."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(author, news):
    """Один комментарий к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def news_items():
    return News.objects.bulk_create([
        News(
            title=f'Новость {i}',
            text='Просто текст',
            date=timezone.now() - timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def comments_for_news(author, news):
    """
    Десять комментариев к одной новости с возрастающими датами,
    возвращает queryset всех комментариев этой новости.
    """
    now = timezone.now()
    for idx in range(10):
        c = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {idx}'
        )
        c.created = now + timedelta(days=idx)
        c.save()
    return Comment.objects.filter(news=news)

@pytest.fixture
def detail_url(news):
    """URL страницы детализации конкретной новости."""
    return reverse('news:detail', args=(news.id,))