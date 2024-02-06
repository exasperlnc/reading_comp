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