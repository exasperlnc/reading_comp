from django.test import TestCase, Client
from django.urls import reverse
from reading_app.models import Document
from reading_app.forms import DocumentForm
from django.core.files.uploadedfile import SimpleUploadedFile

class TestUploadDocument(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('upload_document')

    def test_upload_document_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_app/upload.html')

    def test_upload_document_post(self):
        with open('path/to/your/testfile.txt', 'rb') as file:
            response = self.client.post(self.url, {'docfile': file}, format='multipart')
            self.assertEqual(response.status_code, 302)  # Check for redirect
            self.assertEqual(Document.objects.count(), 1)
