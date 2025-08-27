from django.contrib import admin
from .models import User, Topic, Question, Choice, Test, Attempt, Answer, Bookmark

admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Test)
admin.site.register(Attempt)
admin.site.register(Answer)
admin.site.register(Bookmark)
