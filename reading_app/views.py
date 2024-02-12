from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Document, Question, Answer
from .forms import DocumentForm, AnswerForm
import requests
import openai

def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(file=request.FILES['docfile'])
            newdoc.save()
            return redirect('view_document', document_id=newdoc.id)  # Redirect to the document view
    else:
        form = DocumentForm()
    return render(request, 'reading_app/upload.html', {'form': form})

def generate_questions(document_text):
    try:
        response = requests.post('LLM_API_ENDPOINT', json={
            'text': document_text,
            'other_parameters': '...'
        }, headers={'Authorization': 'Bearer OPEN_AI_API_KEY'})
        response.raise_for_status()
        questions = response.json()  # Assuming the response is JSON with questions
        return questions
    except requests.RequestException as e:
        print(e)
        return []

def view_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    questions = document.question_set.all()
    return render(request, 'reading_app/view_document.html', {'document': document, 'questions': questions})

def submit_answer(request):
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            question = get_object_or_404(Question, pk=form.cleaned_data['question_id'])
            answer = Answer(question=question, user_response=form.cleaned_data['user_answer'])
            answer.save()
            return redirect('answer_success')  # Redirect to a success page or similar
    else:
        form = AnswerForm()
    return render(request, 'reading_app/answer_form.html', {'form': form})

def evaluate_answer_with_gpt3(question_text, user_answer, document_text=None):
    prompt = build_evaluation_prompt(question_text, user_answer, document_text)
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=50
        )
        score = parse_gpt3_response(response.choices[0].text)
        return score
    except openai.error.OpenAIError as e:
        print(e)
        return None

def build_evaluation_prompt(question_text, user_answer, document_text=None):
    prompt = f"Document: {document_text}\n\n" if document_text else ""
    prompt += f"Question: {question_text}\nAnswer: {user_answer}\n\n"
    prompt += "Rate the answer on a scale from 0 (no comprehension) to 5 (full comprehension):"
    return prompt

def parse_gpt3_response(response_text):
    try:
        return int(response_text.strip())
    except ValueError:
        return None

def answer_success(request):
    # Render a template or handle post-answer logic
    return render(request, 'reading_app/answer_success.html')
