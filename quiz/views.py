# quiz/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
# from django.contrib.auth.decorators import login_required  # Commented out temporarily
from .models import Question, Topic,TopicNote
from .forms import QuestionForm, TopicForm
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home(request):
    # Get all topics with their notes and question counts
    topics_with_notes = []
    topics = Topic.objects.all()
    
    for topic in topics:
        try:
            note = topic.note  # Related name from OneToOneField
        except TopicNote.DoesNotExist:
            note = None
            
        topic_data = {
            'topic': topic,
            'note': note,
            'question_count': topic.questions.count()
        }
        topics_with_notes.append(topic_data)
    
    context = {
        'topics_with_notes': topics_with_notes,
    }
    return render(request, 'home.html', context)

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

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Topic, Question
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Topic, Question

def take_quiz(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    questions = list(Question.objects.filter(topic=topic)[:10])
    total_questions = len(questions)

    if total_questions == 0:
        return render(request, "no_questions.html", {"topic": topic})

    # Clear old quiz session if starting new quiz
    start_new = request.GET.get("start", None)
    if start_new:
        if "quiz_answers" in request.session:
            del request.session["quiz_answers"]
        if "quiz_results" in request.session:
            del request.session["quiz_results"]
        if "remaining_seconds" in request.session:
            del request.session["remaining_seconds"]

    # Quiz duration in minutes
    duration_minutes = 10

    # Get current question index
    current_index = int(request.GET.get("q", 0))
    if current_index < 0 or current_index >= total_questions:
        current_index = 0

    # Initialize session for answers
    if "quiz_answers" not in request.session:
        request.session["quiz_answers"] = {}
    answers = request.session["quiz_answers"]

    # Timer: use remaining_seconds from session if exists
    total_seconds = request.session.get("remaining_seconds", duration_minutes * 60)

    if request.method == "POST":
        action = request.POST.get("action")
        current_question = questions[current_index]
        question_id = str(current_question.id)
        user_answer = request.POST.get("answer", "").strip()

        # Save the answer
        answers[question_id] = user_answer
        request.session["quiz_answers"] = answers

        # Update remaining time from hidden input
        remaining_seconds = request.POST.get("remaining_seconds")
        if remaining_seconds:
            request.session["remaining_seconds"] = int(remaining_seconds)

        # Navigation
        if action == "next" and current_index < total_questions - 1:
            return redirect(f"{reverse('take_quiz', args=[topic.id])}?q={current_index + 1}")
        elif action == "prev" and current_index > 0:
            return redirect(f"{reverse('take_quiz', args=[topic.id])}?q={current_index - 1}")
        elif action == "submit":
            # Calculate results
            score = 0
            results = []
            for q in questions:
                q_id = str(q.id)
                user_ans = answers.get(q_id, "").strip()
                correct = (q.correct_option or "").strip()

                if q.question_type in ["MCQ", "TF"]:
                    is_correct = user_ans.upper() == correct.upper() if user_ans else False
                else:
                    is_correct = user_ans == correct

                if is_correct:
                    score += 1

                results.append({
                    "question_text": q.text,
                    "user_answer": user_ans if user_ans else "No answer",
                    "correct_answer": correct,
                    "is_correct": is_correct,
                    "question_type": q.question_type,
                    "options": {
                        "A": q.option_a,
                        "B": q.option_b,
                        "C": q.option_c,
                        "D": q.option_d
                    } if q.question_type == "MCQ" else None
                })

            percentage = (score / total_questions * 100) if total_questions else 0

            request.session["quiz_results"] = {
                "topic_id": topic.id,
                "topic_name": topic.name,
                "score": score,
                "total": total_questions,
                "percentage": round(percentage, 1),
                "results": results
            }

            # Clear answers and timer
            if "quiz_answers" in request.session:
                del request.session["quiz_answers"]
            if "remaining_seconds" in request.session:
                del request.session["remaining_seconds"]

            return redirect('quiz_results')

    # Show current question
    current_question = questions[current_index]
    question_id = str(current_question.id)
    saved_answer = answers.get(question_id, "")

    return render(request, "take_quiz.html", {
        "topic": topic,
        "question": current_question,
        "current_index": current_index,
        "total_questions": total_questions,
        "saved_answer": saved_answer,
        "answered_count": len(answers),
        "unanswered_count": total_questions - len(answers),
        "duration_minutes": duration_minutes,
        "remaining_seconds": total_seconds
    })




from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Topic

def quiz_results(request):
    results_data = request.session.get("quiz_results")
    if not results_data:
        messages.error(request, "No quiz results found.")
        return redirect('select_topic')

    # Fetch topic object
    try:
        topic = Topic.objects.get(name=results_data.get("topic_name"))
    except Topic.DoesNotExist:
        topic = None

    return render(request, "quiz_results.html", {
        "topic": topic,  # Add the topic object
        "score": results_data.get("score"),
        "total": results_data.get("total"),
        "percentage": results_data.get("percentage"),
        "results": results_data.get("results"),
    })


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

def topic_note_create(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Update or create note
            note, created = TopicNote.objects.update_or_create(
                topic=topic,
                defaults={'content': content}
            )
            action = "created" if created else "updated"
            messages.success(request, f'Note {action} successfully for {topic.name}!')
        else:
            messages.error(request, 'Please enter note content.')
    
    return redirect('topic_list')

def topic_note_delete(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    
    if request.method == 'POST':
        try:
            note = topic.note
            note.delete()
            messages.success(request, f'Note deleted for {topic.name}!')
        except TopicNote.DoesNotExist:
            messages.error(request, 'Note not found!')
    
    return redirect('topic_list')

# Update your topic_list view to include notes
def topic_list(request):
    topics = Topic.objects.all()
    # Get all existing notes
    notes = {note.topic_id: note for note in TopicNote.objects.all()}
    
    topics_data = []
    for topic in topics:
        topics_data.append({
            'topic': topic,
            'note': notes.get(topic.id),
            'question_count': topic.questions.count()
        })
    
    return render(request, 'topic_list.html', {
        'topics_data': topics_data,
        'topics': topics  # Keep for compatibility
    })

def topic_note_view(request, topic_id):
    """Display detailed view of a topic with its notes"""
    topic = get_object_or_404(Topic, pk=topic_id)
    
    # Get the note if it exists
    try:
        note = topic.note
    except TopicNote.DoesNotExist:
        note = None
    
    # Get question count and sample questions
    questions = Question.objects.filter(topic=topic)
    question_count = questions.count()
    
    context = {
        'topic': topic,
        'note': note,
        'questions': questions,
        'question_count': question_count,
    }
    
    return render(request, 'topic_note_view.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login user right after registration
            login(request, user)
            return redirect("home")   # we’ll change this later for role-based redirect
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

@login_required
def profile_view(request):
    return render(request, 'profile.html')

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirect_after_login(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect("home")  # Django’s default admin dashboard
    else:
        return redirect("home")     # your quiz home page


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def simple_password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Validation
        if not username or not new_password1 or not new_password2:
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/password_reset.html')
        
        if new_password1 != new_password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/password_reset.html')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'auth/password_reset.html')
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password1)
            user.save()
            messages.success(request, 'Password changed successfully! You can now login.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Username not found.')
            return render(request, 'auth/password_reset.html')
    
    return render(request, 'auth/password_reset.html')