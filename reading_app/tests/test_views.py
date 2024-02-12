from django.test import TestCase, Client
from django.urls import reverse
from reading_app.models import Document, Question, Answer
from reading_app.forms import DocumentForm, AnswerForm
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, Mock
import openai
from reading_app.views import generate_questions
import requests
from django.shortcuts import get_object_or_404
from reading_app.views import evaluate_answer_with_gpt3, build_evaluation_prompt, parse_gpt3_response


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

class SubmitAnswerTests(TestCase):
    def setUp(self):
        self.document = Document.objects.create(
            title="Test Document", 
            file=SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        )

        self.question = Question.objects.create(
            document=self.document, 
            text="Test question"
        )
        self.url = reverse('submit_answer')

    def test_get_submit_answer(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_app/answer_form.html')

    def test_post_submit_answer_valid(self):
        post_data = {
            'question_id': self.question.id,
            'user_answer': 'Test answer'
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)  # Redirect status
        self.assertTrue(Answer.objects.exists())  # Check if the answer was created

    def test_post_submit_answer_valid(self):
        # Data for POST request
        post_data = {
            'question_id': self.question.id,
            'user_answer': 'Test answer'
        }

        # Make POST request and capture response
        response = self.client.post(self.url, post_data)

        # Assert redirect response (which indicates success in your view)
        self.assertEqual(response.status_code, 302)

        # Assert that the answer was created and related to the correct question
        self.assertTrue(Answer.objects.filter(question=self.question, user_response='Test answer').exists())

        # Optionally, verify redirection URL (if 'answer_success' URL is defined)
        # self.assertRedirects(response, reverse('answer_success'))

class EvaluateAnswerWithGPT3Tests(TestCase):
    @patch('reading_app.views.openai.Completion.create')
    def test_evaluate_answer_with_gpt3_successful(self, mock_create):
        # Mock successful API response
        mock_response = Mock()
        mock_response.choices = [Mock(text='Mocked score response')]
        mock_create.return_value = mock_response

        question_text = "What is the capital of France?"
        user_answer = "Paris"
        document_text = "The capital of France is Paris."

        # Call the function
        score = evaluate_answer_with_gpt3(question_text, user_answer, document_text)

        # Assertions
        mock_create.assert_called_once_with(
            engine="davinci",
            prompt=build_evaluation_prompt(question_text, user_answer, document_text),
            max_tokens=50
        )
        self.assertEqual(score, parse_gpt3_response('Mocked score response'))

    @patch('reading_app.views.openai.Completion.create')
    def test_evaluate_answer_with_gpt3_failure(self, mock_create):
        # Mock API failure
        mock_create.side_effect = openai.OpenAIError("API failure")

        question_text = "What is the capital of France?"
        user_answer = "Paris"
        
        # Call the function and assert it returns None on failure
        score = evaluate_answer_with_gpt3(question_text, user_answer)
        self.assertIsNone(score)

