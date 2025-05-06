from django.urls import reverse

NOTE_SLUG = 'test-note'
OTHER_SLUG = 'test-slug'

NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_EDIT_URL = reverse('notes:edit', args=(OTHER_SLUG,))
NOTES_DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))