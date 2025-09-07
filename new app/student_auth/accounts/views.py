import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required

from .models import Student, Contest, Problem, TestCase,  Participant
from .forms import ContestForm, ProblemForm, TestCaseFormSet

# --------------------- Student Auth ---------------------

def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        college = request.POST.get('college')
        passout_year = request.POST.get('passout_year')
        branch = request.POST.get('branch')

        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register')

        Student.objects.create(
            name=name, email=email, password=password,
            mobile=mobile, college=college,
            passout_year=passout_year, branch=branch
        )
        messages.success(request, "Registration successful! Please login.")
        return redirect('home')
    return render(request, 'accounts/register.html')


def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(email=email, password=password)
            request.session['student_id'] = student.id
            return redirect('contest')
        except Student.DoesNotExist:
            messages.error(request, "Invalid credentials")
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    request.session.flush()
    return redirect('home')


def home(request):
    student_id = request.session.get('student_id')
    student = Student.objects.filter(id=student_id).first()
    return render(request, 'accounts/home.html', {'student': student})


def contest(request):
    student_id = request.session.get('student_id')
    student = Student.objects.filter(id=student_id).first()
    return render(request, 'accounts/contest.html', {'student': student})


# --------------------- Admin Panel ---------------------

@staff_member_required
def admin_dashboard(request):
    return render(request, "admin_portal/dashboard.html")


@staff_member_required
def create_contest(request):
    if request.method == "POST":
        cform = ContestForm(request.POST, prefix="contest")
        pform = ProblemForm(request.POST, prefix="problem")
        tformset = TestCaseFormSet(request.POST, prefix="testcases")

        if cform.is_valid() and pform.is_valid() and tformset.is_valid():
            with transaction.atomic():
                contest = cform.save()
                problem = pform.save(commit=False)
                problem.contest = contest
                problem.save()

                for tc in tformset.save(commit=False):
                    tc.problem = problem
                    tc.save()
            return redirect("admin_dashboard")
    else:
        cform = ContestForm(prefix="contest")
        pform = ProblemForm(prefix="problem")
        tformset = TestCaseFormSet(prefix="testcases")

    return render(request, "admin_portal/create_contest.html", {
        "cform": cform, "pform": pform, "tformset": tformset,
    })


@staff_member_required
def delete_contest(request):
    contests = Contest.objects.all()
    if request.method == "POST":
        cid = request.POST.get("contest_id")
        contest = get_object_or_404(Contest, id=cid)
        contest.delete()
        return redirect("admin_dashboard")
    return render(request, "admin_portal/delete_contest.html", {"contests": contests})


@staff_member_required
def partial_evaluate(request):
    contests = Contest.objects.all()
    return render(request, "admin_portal/evaluate.html", {"contests": contests})


# --------------------- Problem Pages ---------------------

def start(request, id=None):
    problems = Problem.objects.all().order_by("id")
    problem = None
    visible_testcases = []

    if id:
        problem = get_object_or_404(Problem, id=id)
        visible_testcases = problem.testcases.filter(is_hidden=False)

    return render(request, "accounts/start.html", {
        "problems": problems,
        "problem": problem,
        "visible_testcases": visible_testcases,  # 👈 frontend ko bheja
    })


# ----------------- RUN CODE -----------------

LANGUAGE_MAP = {
    "python": 71,
    "cpp": 54,
    "c": 50,
    "java": 62,
    "javascript": 63,
}


def run_code(request, problem_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    problem = get_object_or_404(Problem, id=problem_id)
    code = request.POST.get("code")
    language = request.POST.get("language", "python")

    if language not in LANGUAGE_MAP:
        return JsonResponse({"error": "Unsupported language"}, status=400)

    results = []

    for tc in problem.testcases.all():
        # Assuming TestCase model has 'input' and 'expected_output' attributes
        payload = {
            "source_code": code,
            "language_id": LANGUAGE_MAP[language],
            "stdin": getattr(tc, "input", ""),  # safe fallback if missing
            "expected_output": getattr(tc, "expected_output", ""),
        }

        try:
            response = requests.post(
                "http://localhost:2358/submissions?base64_encoded=false&wait=true",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            results.append({
                "input": getattr(tc, "input", ""),
                "output": result.get("stdout"),
                "expected": getattr(tc, "expected_output", ""),
                "status": result.get("status", {}).get("description")
            })
        except Exception as e:
            return JsonResponse({"error": f"Judge0 API failed: {str(e)}"}, status=500)

    return JsonResponse({"results": results})


# ----------------- Get Visible Testcases -----------------

def get_visible_testcases(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    visible_cases = []

    for tc in problem.testcases.all():
        if tc.file and tc.file.path.endswith(".json"):
            with open(tc.file.path, "r") as f:
                try:
                    data = json.load(f)
                    for case in data.get("test_cases", []):
                        if case.get("is_visible", False):
                            visible_cases.append({
                                "test_case_no": case.get("test_case_no"),
                                "stdin": case.get("stdin"),
                                "expected_output": case.get("expected_output")
                            })
                except Exception as e:
                    print("Error reading testcase JSON:", e)

    return JsonResponse({"visible_testcases": visible_cases})
from student_auth.utils.submission_wrapper import SubmissionWrapper

def evaluate_view(request):
    wrapper = SubmissionWrapper("merge_k_lists")
    result = wrapper.evaluate_submission(user_code, "python")
    return JsonResponse(result)

