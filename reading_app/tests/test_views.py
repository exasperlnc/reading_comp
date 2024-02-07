from django.test import TestCase, Client
from django.urls import reverse
from reading_app.models import Document, Question
from reading_app.forms import DocumentForm
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from reading_app.views import generate_questions
import requests
from django.shortcuts import get_object_or_404


class TestUploadDocument(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('upload_document')

    def test_upload_document_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_app/upload.html')

    def test_upload_document_post(self):
        with open('testfile.txt', 'rb') as file:
            response = self.client.post(self.url, {'docfile': file}, format='multipart')
            self.assertEqual(response.status_code, 302)  # Check for redirect
            self.assertEqual(Document.objects.count(), 1)
class GenerateQuestionsTests(TestCase):
    @patch('reading_app.views.requests.post')
    def test_generate_questions_successful(self, mock_post):
        # Mock successful API response
        mock_response = mock_post.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = ['Question 1', 'Question 2']

        # Call the function
        questions = generate_questions("Sample document text")

        # Assertions
        self.assertEqual(questions, ['Question 1', 'Question 2'])
        mock_post.assert_called_once_with(
            'LLM_API_ENDPOINT',
            json={'text': 'Sample document text', 'other_parameters': '...'},
            headers={'Authorization': 'Bearer OPEN_AI_API_KEY'}
        )

    @patch('reading_app.views.requests.post')
    def test_generate_questions_failure(self, mock_post):
        # Mock API failure
        mock_post.side_effect = requests.RequestException("API failure")

        # Call the function
        questions = generate_questions("Sample document text")

        # Assertions
        self.assertEqual(questions, [])
class ViewDocumentTests(TestCase):
    def setUp(self):
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")

        self.document = Document.objects.create(title="Test Document", file=test_file)

        self.url = reverse('view_document', args=(self.document.id,))

    def test_view_document_with_existing_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_app/view_document.html')
        self.assertIn('document', response.context)
        self.assertIn('questions', response.context)
        self.assertEqual(response.context['document'], self.document)

    def test_view_document_with_non_existing_id(self):
        non_existing_id_url = reverse('view_document', args=(999,))
        response = self.client.get(non_existing_id_url)
        self.assertEqual(response.status_code, 404)

