# quiz/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
# from django.contrib.auth.decorators import login_required  # Commented out temporarily
from .models import Question, Topic
from .forms import QuestionForm, TopicForm

def home(request):
    return render(request, 'home.html')

# Topic Views
# @login_required  # Commented out temporarily
def topic_list(request):
    topics = Topic.objects.all()
    return render(request, 'topic_list.html', {'topics': topics})

# @login_required  # Commented out temporarily
def topic_create(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Topic created successfully!')
            return redirect('topic_list')
    else:
        form = TopicForm()
    return render(request, 'topic_form.html', {'form': form})

# @login_required  # Commented out temporarily
def topic_edit(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, 'Topic updated successfully!')
            return redirect('topic_list')
    else:
        form = TopicForm(instance=topic)
    return render(request, 'topic_form.html', {'form': form})

# @login_required  # Commented out temporarily
def topic_delete(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == 'POST':
        topic.delete()
        messages.success(request, 'Topic deleted successfully!')
        return redirect('topic_list')
    return render(request, 'topic_confirm_delete.html', {'topic': topic})

# Question Views
# @login_required  # Commented out temporarily
def question_list(request):
    questions = Question.objects.all().select_related('topic')
    return render(request, 'question_list.html', {'questions': questions})

# @login_required  # Commented out temporarily
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            # question.created_by = request.user  # Commented out temporarily
            
            # Clear MCQ options if not MCQ type
            if question.question_type != 'MCQ':
                question.option_a = None
                question.option_b = None
                question.option_c = None
                question.option_d = None
            
            question.save()
            messages.success(request, 'Question created successfully!')
            return redirect('question_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuestionForm()
    
    return render(request, 'question_form.html', {'form': form})

# @login_required  # Commented out temporarily
def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            
            # Clear MCQ options if not MCQ type
            if question.question_type != 'MCQ':
                question.option_a = None
                question.option_b = None
                question.option_c = None
                question.option_d = None
            
            question.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('question_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'question_form.html', {'form': form})

# @login_required  # Commented out temporarily
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('question_list')
    return render(request, 'question_confirm_delete.html', {'question': question})

# Quiz functionality
# @login_required  # Commented out temporarily
def select_topic(request):
    topics = Topic.objects.all()
    return render(request, 'select_topic.html', {'topics': topics})

# @login_required  # Commented out temporarily
# Add this to your quiz/views.py file

# Replace your existing take_quiz function with this updated version:

def take_quiz(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    questions = Question.objects.filter(topic=topic)[:10]  # Limit to 10 questions
    
    if request.method == 'POST':
        # Handle quiz submission
        score = 0
        total_questions = len(questions)
        results = []
        
        for question in questions:
            user_answer = request.POST.get(str(question.id))
            correct_answer = question.correct_option
            is_correct = False
            
            if user_answer and correct_answer:
                if user_answer.upper() == correct_answer.upper():
                    score += 1
                    is_correct = True
            
            results.append({
                'question': question,  # This is fine for direct template rendering
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct
            })
        
        # Calculate percentage
        percentage = (score / total_questions * 100) if total_questions > 0 else 0
        
        # Render results directly instead of redirecting
        return render(request, 'quiz_results.html', {
            'topic': topic,
            'score': score,
            'total': total_questions,
            'percentage': round(percentage, 1),
            'results': results
        })
    
    # Handle GET request (display quiz)
    return render(request, 'take_quiz.html', {
        'topic': topic, 
        'questions': questions
    })

# Add this new view for displaying results
def quiz_results(request):
    results_data = request.session.get('quiz_results')
    if not results_data:
        messages.error(request, 'No quiz results found.')
        return redirect('select_topic')
    
    return render(request, 'quiz_results.html', {'results': results_data})

# Optional: Add this view to retake quiz
def retake_quiz(request, topic_id):
    # Clear any existing results
    if 'quiz_results' in request.session:
        del request.session['quiz_results']
    return redirect('take_quiz', topic_id=topic_id)

# NEW PRACTICE SECTION VIEWS
# @login_required  # Commented out temporarily
def practice_select_topic(request):
    """Select topic for practice session"""
    topics = Topic.objects.annotate(
        question_count=Count('questions')
    ).filter(question_count__gt=0)  # Only show topics with questions
    return render(request, 'practice_select_topic.html', {'topics': topics})

# @login_required  # Commented out temporarily
def practice_questions(request, topic_id):
    """Display practice questions with solutions for a topic"""
    topic = get_object_or_404(Topic, pk=topic_id)
    
    # Get all questions for this topic
    questions_list = Question.objects.filter(topic=topic).order_by('difficulty', 'created_at')
    
    # Add pagination
    paginator = Paginator(questions_list, 5)  # Show 5 questions per page
    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)
    
    # Get difficulty filter if provided
    difficulty_filter = request.GET.get('difficulty')
    if difficulty_filter:
        questions_list = questions_list.filter(difficulty=difficulty_filter)
        questions = paginator.get_page(page_number)
    
    return render(request, 'practice_questions.html', {
        'topic': topic,
        'questions': questions,
        'difficulty_levels': Question.DIFFICULTY_LEVELS,
        'current_difficulty': difficulty_filter
    })

# @login_required  # Commented out temporarily  
def practice_question_detail(request, question_id):
    """Display a single practice question with detailed solution"""
    question = get_object_or_404(Question, pk=question_id)
    
    # Get related questions from the same topic (for navigation)
    related_questions = Question.objects.filter(
        topic=question.topic
    ).exclude(pk=question.pk)[:5]
    
    return render(request, 'practice_question_detail.html', {
        'question': question,
        'related_questions': related_questions
    })