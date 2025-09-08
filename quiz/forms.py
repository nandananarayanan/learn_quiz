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
            'option_a', 'option_b', 'option_c', 'option_d',
            'correct_option', 'solution'
        ]
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_question_type'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'option_a': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Option A'}),
            'option_b': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Option B'}),
            'option_c': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Option C'}),
            'option_d': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Option D'}),
            'solution': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter solution (LaTeX supported)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make MCQ options not required by default
        self.fields['option_a'].required = False
        self.fields['option_b'].required = False
        self.fields['option_c'].required = False
        self.fields['option_d'].required = False
        self.fields['correct_option'].required = False

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        
        # Validate based on question type
        if question_type == 'MCQ':
            # For MCQ, all options should be filled
            required_fields = ['option_a', 'option_b', 'option_c', 'option_d']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required for MCQ questions.')
            
            # Validate correct option for MCQ
            correct_option = cleaned_data.get('correct_option')
            if correct_option not in ['A', 'B', 'C', 'D']:
                self.add_error('correct_option', 'For MCQ questions, correct option must be A, B, C, or D.')
        
        elif question_type == 'TF':  # True/False
            # For True/False, options are not needed
            correct_option = cleaned_data.get('correct_option')
            if correct_option not in ['True', 'False']:
                self.add_error('correct_option', 'For True/False questions, correct option must be True or False.')
        
        elif question_type == 'NUM':  # Numeric
            # For Numeric, correct_option should contain the numeric answer
            correct_option = cleaned_data.get('correct_option')
            if not correct_option:
                self.add_error('correct_option', 'Please provide the correct numeric answer.')
        
        return cleaned_data

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()  # THIS will point to quiz.User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User  # Now this is your quiz.User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
