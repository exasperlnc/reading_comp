from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Select a file')

    from django import forms

class AnswerForm(forms.Form):
    user_answer = forms.CharField(widget=forms.Textarea, label='Your Answer')
    question_id = forms.IntegerField(widget=forms.HiddenInput())
