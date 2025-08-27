from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Question
from .forms import TopicForm, QuestionForm

def home(request):
    return render(request, "home.html")

# ---------------- TOPIC ----------------
def topic_list(request):
    topics = Topic.objects.all()
    return render(request, "topic_list.html", {"topics": topics})

def topic_create(request):
    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("topic_list")
    else:
        form = TopicForm()
    return render(request, "topic_form.html", {"form": form})

def topic_edit(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == "POST":
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return redirect("topic_list")
    else:
        form = TopicForm(instance=topic)
    return render(request, "topic_form.html", {"form": form})

def topic_delete(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == "POST":
        topic.delete()
        return redirect("topic_list")
    return render(request, "topic_confirm_delete.html", {"topic": topic})

# ---------------- QUESTION ----------------
def question_list(request):
    questions = Question.objects.all()
    return render(request, "question_list.html", {"questions": questions})

def question_create(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("question_list")
    else:
        form = QuestionForm()
    return render(request, "question_form.html", {"form": form})

def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect("question_list")
    else:
        form = QuestionForm(instance=question)
    return render(request, "question_form.html", {"form": form})

def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        question.delete()
        return redirect("question_list")
    return render(request, "question_confirm_delete.html", {"question": question})
