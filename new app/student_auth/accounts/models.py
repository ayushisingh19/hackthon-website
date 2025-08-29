from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


# ----------------- Student Model -----------------
class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)  # Should be hashed!
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
    description = models.TextField(blank=True, null=True)  # Added description field
    
    # Separate fields for answers and memory limits
    cpp_answer = models.TextField(blank=True, null=True)
    python_answer = models.TextField(blank=True, null=True)
    cpp_mem_limit_mb = models.PositiveIntegerField(default=256)
    python_mem_limit_mb = models.PositiveIntegerField(default=256)

    class Meta:
        unique_together = ("contest", "code")

    def __str__(self):
        return f"{self.contest.name}: {self.code} - {self.title}"


    class Meta:
        unique_together = ("contest", "code")

    def __str__(self):
        return f"{self.contest.name}: {self.code} - {self.title}"


# ----------------- TestCase Model -----------------
class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="testcases")
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.problem.code} ({'hidden' if self.is_hidden else 'visible'})"


# ----------------- Submission Model -----------------
class Submission(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    language = models.CharField(max_length=30, default="python")
    code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Evaluation Results
    is_correct = models.BooleanField(default=False)
    inferred_complexity = models.CharField(max_length=20, default="O(n)")
    fit_error = models.FloatField(default=0.0)
    const_C = models.FloatField(default=1.0)
    peak_mem_mb = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Submission by {self.participant.handle} for {self.problem.code}"


# ----------------- ScoreboardRow Model -----------------
class ScoreboardRow(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    problems_scores = models.JSONField(default=dict)  # {"P1": 100.0, "P2": 50.0, ...}

    @property
    def total_submitted(self):
        return len(self.problems_scores)

    def score_for(self, code):
        return self.problems_scores.get(code, 0.0)

    class Meta:
        unique_together = ("contest", "participant")

    def __str__(self):
        return f"{self.participant.handle} - {self.contest.name}"


# ----------------- Optional: Language Map -----------------
# If used in views
LANGUAGE_MAP = {
    "python": 71,
    "cpp": 54,
    "c": 50,
    "java": 62,
    "javascript": 63,
}
