import pytest

from django.test.client import Client

from notes.models import Note


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Not Author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def note(author):
    note = Note.objects.create(
        title='Note title',
        text='Note text',
        slug='note-slug',
        author=author,
    )
    return note


@pytest.fixture
def slug_for_args(note):
    return (note.slug, )


@pytest.fixture
def form_data():
    return {
        'title': 'New note title',
        'text': 'New note text',
        'slug': 'new-slug',
    }

