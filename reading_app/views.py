from django.shortcuts import render
from .models import Document
from .forms import DocumentForm

def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(file=request.FILES['docfile'])
            newdoc.save()
            # After saving, redirect to a new URL or indicate success
    else:
        form = DocumentForm()

    return render(request, 'reading_app/upload.html', {'form': form})

    import requests

def generate_questions(document_text):
    response = requests.post('LLM_API_ENDPOINT', json={
        'text': document_text,
        'other_parameters': '...'
    }, headers={'Authorization': 'Bearer OPEN_AI_API_KEY'})

    questions = response.json()  # Assuming the response is JSON with questions
    return questions

    from django.shortcuts import render, get_object_or_404

def view_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    questions = document.question_set.all()
    return render(request, 'reading_app/view_document.html', {'document': document, 'questions': questions})
# Path: reading_app/urls.py

def submit_answer(request):
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            question = get_object_or_404(Question, pk=form.cleaned_data['question_id'])
            answer = Answer(question=question, user_response=form.cleaned_data['user_answer'])
            answer.save()
            # Redirect or show some confirmation page
    else:
        form = AnswerForm()

    return render(request, 'reading_app/answer_form.html', {'form': form})

import openai

def evaluate_answer_with_gpt3(question_text, user_answer, document_text=None):
    prompt = build_evaluation_prompt(question_text, user_answer, document_text)
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50  # Adjust as necessary
    )
    score = parse_gpt3_response(response.choices[0].text)
    return score

def build_evaluation_prompt(question_text, user_answer, document_text=None):
    prompt = f"Document: {document_text}\n\n" if document_text else ""
    prompt += f"Question: {question_text}\nAnswer: {user_answer}\n\n"
    prompt += "Rate the answer on a scale from 0 (no comprehension) to 5 (full comprehension):"
    return prompt

def parse_gpt3_response(response_text):
    # Implement logic to parse the score from GPT-3's response
    # Example: assuming GPT-3 returns a simple number as a response
    try:
        return int(response_text.strip())
    except ValueError:
        return None  # or handle as appropriate

