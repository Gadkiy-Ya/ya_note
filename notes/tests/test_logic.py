from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.form_data = {
            'title': 'Note title',
            'text': 'Note text',
            'slug': 'note-slug',
        }

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.first()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)
    
    def test_anonymous_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 0)


class TestSlug(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.note = Note.objects.create(
            title='Note title',
            text='Note text',
            slug='note-slug',
            author=cls.author
        )

    def test_slug_not_unique(self):
        form_data = {
            'title': 'New note title',
            'text': 'New note text',
            'slug': 'note-slug',
        }
        self.assertEqual(Note.objects.count(), 1)
        self.client.force_login(self.author)
        url = reverse('notes:add')
        # form_data['slug'] = 'note-slug'
        response = self.client.post(url, data=form_data)
        self.assertFormError(response, 'form', 'slug', errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)
    
    def test_slug_empty(self):
        form_data = {
            'title': 'New note title',
            'text': 'New note text',
            'slug': '',
        }
        self.assertEqual(Note.objects.count(), 1)
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.last()
        self.assertEqual(new_note.slug, slugify(form_data['title']))
    

class TestEditDeleteNote(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.another_user = User.objects.create(username='Another user')
        cls.note = Note.objects.create(
            title='Note title',
            text='Note text',
            slug='note-slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'New note title',
            'text': 'New note text',
            'slug': 'new-slug',
        }

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        self.assertEqual(Note.objects.count(), 1)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(Note.objects.count(), 1)
    
    def test_another_user_cant_edit_note(self):
        self.client.force_login(self.another_user)
        self.assertEqual(Note.objects.count(), 1)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_another_user_cant_delete_note(self):
        self.client.force_login(self.another_user)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
