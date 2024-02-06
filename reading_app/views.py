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
