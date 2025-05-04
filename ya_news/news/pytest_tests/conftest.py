# conftest.py
import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client

from news.models import News, Comment


User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
@pytest.mark.django_db
def author():
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
@pytest.mark.django_db
def reader():
    return User.objects.create(username='Читатель простой')


@pytest.fixture
@pytest.mark.django_db
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
@pytest.mark.django_db
def news_id(news):
    return (news.id,)


@pytest.fixture
@pytest.mark.django_db
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
@pytest.mark.django_db
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
@pytest.mark.django_db
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
@pytest.mark.django_db
def form_data():
    return {'text': 'Новый текст'}
