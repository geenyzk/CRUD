from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Record


class RecordCrudTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staff', password='test-pass', is_staff=True
        )
        self.client.login(username='staff', password='test-pass')

    def test_staff_can_create_record(self):
        response = self.client.post(
            reverse('record_create'),
            {'title': 'Example', 'description': 'Details'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Record.objects.filter(title='Example').exists())

    def test_staff_can_update_record(self):
        record = Record.objects.create(title='Initial', description='Old', created_by=self.staff_user)
        response = self.client.post(
            reverse('record_update', args=[record.pk]),
            {'title': 'Updated', 'description': 'New description'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        record.refresh_from_db()
        self.assertEqual(record.title, 'Updated')
        self.assertEqual(record.description, 'New description')

    def test_staff_can_delete_record(self):
        record = Record.objects.create(title='Temp', created_by=self.staff_user)
        response = self.client.post(reverse('record_delete', args=[record.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Record.objects.filter(pk=record.pk).exists())

    def test_search_filters_records(self):
        record_keep = Record.objects.create(title='Launch Plan', description='Q1 rollout', created_by=self.staff_user)
        Record.objects.create(title='Archive', description='Deprecated', created_by=self.staff_user)

        response = self.client.get(reverse('records_list'), {'q': 'launch'})
        self.assertContains(response, record_keep.title)
        self.assertNotContains(response, 'Archive')
