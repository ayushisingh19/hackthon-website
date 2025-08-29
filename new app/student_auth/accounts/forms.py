from django import forms
from .models import Contest, Problem, TestCase
from django.forms import inlineformset_factory


class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ["name", "start_at", "duration_minutes", "is_active"]
        widgets = {
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = [
            "contest",
            "code",
            "title",
            "description",
            "cpp_answer",
            "cpp_mem_limit_mb",
            "python_answer",
            "python_mem_limit_mb",
        ]


TestCaseFormSet = inlineformset_factory(
    Problem,
    TestCase,
    fields=["input_data", "expected_output", "is_hidden"],
    extra=1,
    can_delete=True,
)
