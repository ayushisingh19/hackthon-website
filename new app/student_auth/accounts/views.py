import json
import time
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required

from .models import Student, Contest, Problem, TestCase, ScoreboardRow, Submission, Participant
from .forms import ContestForm, ProblemForm, TestCaseFormSet
from .scoring import final_score

# Judge0 API details
JUDGE0_SUBMIT_URL = "https://judge0.p.rapidapi.com/submissions?base64_encoded=false&wait=false"
JUDGE0_GET_URL = "https://judge0.p.rapidapi.com/submissions"
JUDGE0_HEADERS = {
    "X-RapidAPI-Host": "judge0.p.rapidapi.com",
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY_HERE",  # Replace with your RapidAPI key
    "Content-Type": "application/json"
}

LANGUAGE_MAP = {
    "python": 71,
    "cpp": 54,
    "c": 50,
    "java": 62,
    "javascript": 63,
}

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


@staff_member_required
@require_POST
def api_start_evaluation(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    problems = Problem.objects.filter(contest=contest).prefetch_related("testcases")
    participants = Participant.objects.all()

    # Delete old scoreboard entries
    ScoreboardRow.objects.filter(contest=contest).delete()

    for participant in participants:
        scores = {}
        for problem in problems:
            # Dummy scoring, replace with actual evaluation logic
            scores[problem.code] = final_score([1, 0, 1], problem.testcases.count())
        ScoreboardRow.objects.create(
            contest=contest,
            participant=participant,
            problems_scores=scores
        )
    return JsonResponse({"status": "ok"})


@staff_member_required
def api_scoreboard(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    rows = ScoreboardRow.objects.filter(contest=contest).order_by("participant__handle")
    data = [
        {
            "participant": r.participant.handle,
            "scores": r.problems_scores,
            "total": sum(r.problems_scores.values())
        }
        for r in rows
    ]
    return JsonResponse({"rows": data})

# --------------------- Problems & Submission ---------------------

def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    testcases = problem.testcases.all()
    all_problems = Problem.objects.all()
    return render(request, 'problem_detail.html', {
        'problem': problem,
        'testcases': testcases,
        'all_problems': all_problems,
    })


@csrf_exempt
def submit_code(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    problem_id = request.POST.get("problem_id")
    code = request.POST.get("code")
    language = request.POST.get("language", "python")
    participant_id = request.POST.get("participant_id")

    if not problem_id or not code:
        return HttpResponseBadRequest("Missing required fields")

    problem = get_object_or_404(Problem, id=problem_id)
    if participant_id:
        participant = get_object_or_404(Participant, id=participant_id)
    else:
        participant = Participant.objects.first()

    if not participant:
        return JsonResponse({"status": "error", "message": "No participant found."}, status=400)

    language_id = LANGUAGE_MAP.get(language)
    if not language_id:
        return HttpResponseBadRequest("Unsupported language")

    testcases = problem.testcases.all()
    passed = 0
    results = []

    for testcase in testcases:
        result, error = run_code_on_judge0(code, language_id, testcase.input_data)
        if error:
            return JsonResponse({"status": "error", "message": error}, status=500)

        output = (result.get("stdout") or "").strip()
        expected = testcase.expected_output.strip()
        is_correct = (output == expected)
        if is_correct:
            passed += 1

        results.append({
            "input": testcase.input_data,
            "expected": expected,
            "output": output,
            "status": "Passed" if is_correct else "Failed",
            "time": result.get("time"),
            "memory": result.get("memory")
        })

    final_score_val = (passed / len(testcases)) * 100 if testcases else 0

    Submission.objects.create(
        participant=participant,
        problem=problem,
        code=code,
        language=language,
        is_correct=(passed == len(testcases)),
        final_score=final_score_val,
    )

    return JsonResponse({
        "status": "success",
        "message": f"Passed {passed} / {len(testcases)} test cases.",
        "results": results,
        "final_score": final_score_val
    })


def run_code_on_judge0(source_code, language_id, input_data):
    data = {
        "language_id": language_id,
        "source_code": source_code,
        "stdin": input_data,
        "cpu_time_limit": 2,
        "memory_limit": 128000,
    }
    response = requests.post(JUDGE0_SUBMIT_URL, headers=JUDGE0_HEADERS, data=json.dumps(data))
    if response.status_code != 201:
        return None, "Judge0 API error"

    token = response.json().get("token")
    result_url = f"{JUDGE0_GET_URL}/{token}?base64_encoded=false"

    for _ in range(10):
        res = requests.get(result_url, headers=JUDGE0_HEADERS)
        if res.status_code == 200:
            result = res.json()
            # Status IDs:
            # 1: In Queue, 2: Processing, 3: Accepted, 4+: Various errors
            if result['status']['id'] in [1, 2]:  # still running
                time.sleep(1)
                continue
            return result, None

    return None, "Timeout waiting for Judge0 result"

# --------------------- Problem Editor ---------------------

def problem_editor_view(request, slug=None):
    problems = Problem.objects.all()
    problem = None

    if slug:
        problem = get_object_or_404(Problem, slug=slug)

    return render(request, 'accounts/problem_editor.html', {
        'problems': problems,
        'problem': problem
    })

@csrf_exempt
def run_code(request):
    if request.method == "POST":
        code = request.POST.get("code")
        language = request.POST.get("language")
        problem_id = request.POST.get("problem_id")

        if not all([code, language, problem_id]):
            return JsonResponse({"error": "Missing parameters"}, status=400)

        problem = get_object_or_404(Problem, id=problem_id)
        language_id = LANGUAGE_MAP.get(language)
        if not language_id:
            return JsonResponse({"error": "Unsupported language"}, status=400)

        results = []
        for testcase in problem.testcases.all():
            result, error = run_code_on_judge0(code, language_id, testcase.input_data)
            if error:
                return JsonResponse({"error": error}, status=500)

            output = (result.get("stdout") or "").strip()
            expected = testcase.expected_output.strip()
            passed = output == expected

            results.append({
                "input": testcase.input_data,
                "expected": expected,
                "output": output,
                "passed": passed,
                "time": result.get("time"),
                "memory": result.get("memory")
            })

        return JsonResponse({"results": results})

    return JsonResponse({"error": "Invalid request"}, status=400)
from django.shortcuts import render, get_object_or_404
from .models import Problem

def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    testcases = problem.testcases.all()
    all_problems = Problem.objects.all()
    return render(request, 'accounts/problem_detail.html', {
        'problem': problem,
        'testcases': testcases,
        'all_problems': all_problems,
    })

