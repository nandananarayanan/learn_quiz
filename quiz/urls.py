from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # Topic URLs
    path("topics/", views.topic_list, name="topic_list"),
    path("topics/add/", views.topic_create, name="topic_create"),
    path("topics/<int:pk>/edit/", views.topic_edit, name="topic_edit"),
    path("topics/<int:pk>/delete/", views.topic_delete, name="topic_delete"),

    # Question URLs
    path("questions/", views.question_list, name="question_list"),
    path("questions/add/", views.question_create, name="question_create"),
    path("questions/<int:pk>/edit/", views.question_edit, name="question_edit"),
    path("questions/<int:pk>/delete/", views.question_delete, name="question_delete"),
]
