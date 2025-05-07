from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def home_url():
    """URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """URL входа автора."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """URL выхода автора."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """URL регистрации автора."""
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    """URL страницы новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def detail_url_with_comments(detail_url):
    """URL страницы новости с якорем на комментарии."""
    return f'{detail_url}#comments'


@pytest.fixture
def delete_url(comment):
    """URL удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def delete_login_redirect(delete_url, login_url):
    return f"{login_url}?next={delete_url}"


@pytest.fixture
def edit_url(comment):
    """URL редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def edit_login_redirect(edit_url, login_url):
    return f"{login_url}?next={edit_url}"


@pytest.fixture
def author():
    """Пользователь-автор комментариев."""
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
def reader():
    """Пользователь-читатель комментариев."""
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
    """
    Создаёт в базе на +1 новость больше, чем отображается на главной странице:
    NEWS_COUNT_ON_HOME_PAGE + 1 объектов News с постепенным уменьшением даты.
    Полезно для проверки количества и порядка вывода новостей.
    """
    News.objects.bulk_create(
        News(
            title=f'Новость {i}',
            text='Просто текст',
            date=timezone.now() - timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


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
