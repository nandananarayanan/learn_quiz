from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # Topic URLs
    path("topics/", views.topic_list, name="topic_list"),
    path("topics/add/", views.topic_create, name="topic_create"),
    path("topics/<int:pk>/edit/", views.topic_edit, name="topic_edit"),
    path("topics/<int:pk>/delete/", views.topic_delete, name="topic_delete"),

    path("topics/<int:topic_id>/note/add/", views.topic_note_create, name="topic_note_create"),
    path("topics/<int:topic_id>/note/delete/", views.topic_note_delete, name="topic_note_delete"),
    path('topic/<int:topic_id>/notes/', views.topic_note_view, name='topic_note_view'),

    # Question URLs
    path("questions/", views.question_list, name="question_list"),
    path("questions/add/", views.question_create, name="question_create"),
    path("questions/<int:pk>/edit/", views.question_edit, name="question_edit"),
    path("questions/<int:pk>/delete/", views.question_delete, name="question_delete"),

    path("select-topic/", views.select_topic, name="select_topic"),
    path('quiz/<int:topic_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/results/', views.quiz_results, name='quiz_results'),

    path("practice/", views.practice_select_topic, name="practice_select_topic"),
    path("practice/<int:topic_id>/", views.practice_questions, name="practice_questions"),  
    path("practice/question/<int:question_id>/", views.practice_question_detail, name="practice_question_detail"),
]
