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
          
        ]


TestCaseFormSet = inlineformset_factory(
    Problem,
    TestCase,
    fields=["language", "file"],  # ✅ updated fields
    extra=1,
    can_delete=True,
)
