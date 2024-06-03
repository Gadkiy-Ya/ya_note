

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesContent(TestCase):
    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
      
        cls.author = User.objects.create(username='Author')
        cls.another_user = User.objects.create(username='Another user')
        cls.note = Note.objects.create(
            title='Note title',
            text='Note text',
            author=cls.author,
            slug='note-slug'
        )
 
    def test_note_is_in_notes_list_for_author(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
    
    def test_note_is_not_in_notes_list_for_another_user(self):
        self.client.force_login(self.another_user)
        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)
    
    def test_create_note_page_contains_form(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
    
    def test_edit_note_page_contains_form(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:edit', args=(self.note.slug,)))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)