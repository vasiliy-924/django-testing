from django.urls import reverse

NOTE_SLUG = 'test-note'
OTHER_SLUG = 'test-slug'

NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_SUCCESS_URL = reverse('notes:success')

NOTES_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
NOTES_DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))

OTHER_EDIT_URL = reverse('notes:edit', args=(OTHER_SLUG,))
OTHER_DELETE_URL = reverse('notes:delete', args=(OTHER_SLUG,))
