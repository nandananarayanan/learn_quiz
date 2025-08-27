# quiz/forms.py
from django import forms
from .models import Question, Topic

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name',]

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'topic', 'text', 'question_type', 'difficulty',
            'marks', 'negative_marks'
        ]
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'negative_marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }
