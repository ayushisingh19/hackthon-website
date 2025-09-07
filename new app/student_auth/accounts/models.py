from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import os

User = get_user_model()


# ----------------- Student Model -----------------
class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)  # TODO: hash this in production
    mobile = models.CharField(max_length=15)
    college = models.CharField(max_length=200)
    passout_year = models.IntegerField()
    branch = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ----------------- Participant Model -----------------
class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=120)
    handle = models.CharField(max_length=64, unique=True)
    is_disqualified = models.BooleanField(default=False)

    def __str__(self):
        return self.handle or self.name


# ----------------- Contest Model -----------------
class Contest(models.Model):
    name = models.CharField(max_length=200)
    start_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def end_at(self):
        return self.start_at + timezone.timedelta(minutes=self.duration_minutes)


# ----------------- Problem Model -----------------
class Problem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="problems")
    code = models.CharField(max_length=30)  # e.g., P1, P2
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)

    difficulty = models.CharField(
        max_length=20,
        choices=[("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")],
        default="Easy"
    )
    constraints = models.TextField(blank=True, null=True)


    class Meta:
        unique_together = ("contest", "code")

    def __str__(self):
        return f"{self.contest.name}: {self.code} - {self.title}"


# ----------------- TestCase Model -----------------
def testcase_upload_path(instance, filename):
    """
    Custom path: media/testcases/problem_<id>/<language>_<filename>
    Example: media/testcases/problem_1/python_sample.json
    """
    return os.path.join(
        "testcases",
        f"problem_{instance.problem.id}",
        f"{instance.language}_{filename}"
    )


class TestCase(models.Model):
    LANGUAGE_CHOICES = [
        ("python", "Python"),
        ("cpp", "C++"),
        ("java", "Java"),
    ]

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="testcases")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    file = models.FileField(upload_to=testcase_upload_path)  # saved on server
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.problem.code} - {self.language}"


