from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ---------------------------
# 1. Custom User Model
# ---------------------------
class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)

    def __str__(self):
        return self.username


# ---------------------------
# 2. Topic (Percentage, Profit & Loss, etc.)
# ---------------------------
class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ---------------------------
# 3. Question (MCQ, True/False, Numeric types supported)
# ---------------------------
class Question(models.Model):
    QUESTION_TYPES = [
        ("MCQ", "Multiple Choice"),
        ("NUM", "Numeric"),
        ("TF", "True/False"),
    ]

    DIFFICULTY_LEVELS = [
        (1, "Easy"),
        (2, "Medium"),
        (3, "Hard"),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()  # Question text (can hold LaTeX)
    question_type = models.CharField(max_length=5, choices=QUESTION_TYPES, default="MCQ")
    difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS, default=1)
    marks = models.FloatField(default=1.0, editable=False)

    # MCQ options (only used when question_type is MCQ)
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)

    # Correct answer for all question types
    correct_option = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=(
            "For MCQ: enter A, B, C, or D; "
            "For True/False: enter True or False; "
            "For Numeric: enter the number as text."
        )
    )

    # LaTeX solution / step-by-step explanation
    solution = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

    def get_correct_answer_display(self):
        """Return a human-readable format of the correct answer"""
        if self.question_type == 'MCQ':
            options_map = {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d
            }
            return f"{self.correct_option}: {options_map.get(self.correct_option, 'Unknown')}"
        elif self.question_type == 'TF':
            return self.correct_option
        elif self.question_type == 'NUM':
            return self.correct_option
        return self.correct_option


# ---------------------------
# 4. Choice (for MCQs) - This can be kept for backward compatibility
# ---------------------------
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"


# ---------------------------
# 5. Test (Daily / Weekly test instance)
# ---------------------------
class Test(models.Model):
    TEST_TYPES = [
        ("DAILY", "Daily Test"),
        ("WEEKLY", "Weekly Test"),
        ("CUSTOM", "Custom Test"),
    ]

    name = models.CharField(max_length=100)
    test_type = models.CharField(max_length=10, choices=TEST_TYPES, default="CUSTOM")
    topics = models.ManyToManyField(Topic, blank=True)
    num_questions = models.IntegerField(default=10)
    duration_minutes = models.IntegerField(default=30)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.test_type})"


# ---------------------------
# 6. Attempt (Student taking a test or practice session)
# ---------------------------
class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f"Attempt by {self.user} on {self.test}"


# ---------------------------
# 7. Answer (Student's response)
# ---------------------------
class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    typed_answer = models.CharField(max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.FloatField(default=0.0)

    def __str__(self):
        return f"Answer to {self.question} by {self.attempt.user}"


# ---------------------------
# 8. Bookmark (Students can save questions for later review)
# ---------------------------
class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user} bookmarked {self.question.id}"