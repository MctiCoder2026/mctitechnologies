
import re
from types import SimpleNamespace

from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from core.models import Enquiry
from .views import TYPING_BRANCHES

DATA = [
    ("home-row", "Home Row Basics",
     "asdf jkl; asdf jkl; aaa sss ddd fff jjj kkk lll ;;; "
     "sad lad dad fall ask flask salad"),
    ("top-row", "Top Row Practice",
     "qwer tyui op qwer tyui op quiet type write power "
     "quote trip wire tower proper"),
    ("bottom-row", "Bottom Row Practice",
     "zxcv bnm zxcv bnm zip mix van box next move "
     "zoom back nice voice never"),
    ("common-words", "Everyday English Words",
     "learn work study practice school office computer "
     "keyboard student teacher time skill future success"),
    ("short-paragraphs", "Short English Paragraphs",
     "Regular practice builds confidence. Keep your eyes on the screen "
     "and use both hands. Focus on accuracy first. Your typing speed "
     "will improve as you practise every day."),
]

LESSONS = [
    SimpleNamespace(
        slug=slug, title=title, content=text, order=i,
        target_wpm=10 if i <= 3 else 20, target_accuracy=90,
    )
    for i, (slug, title, text) in enumerate(DATA, 1)
]


def home(request):
    progress = request.session.get("typing_free_progress", {})
    rows = []
    for lesson in LESSONS:
        rows.append({
            "lesson": lesson,
            "result": progress.get(lesson.slug),
        })
    return render(request, "typing_practice/public_typing.html", {
        "rows": rows,
        "registered": request.session.get("typing_public_registered", False),
        "guest_name": request.session.get("typing_public_name", ""),
    })


def practice(request, slug):
    lesson = next((x for x in LESSONS if x.slug == slug), None)
    if lesson is None:
        raise Http404("Free lesson not found.")
    if lesson.order > 2 and not request.session.get("typing_public_registered"):
        return redirect("typing_practice:public_register")
    return render(request, "typing_practice/public_practice.html", {
        "lesson": lesson,
        "registered": request.session.get("typing_public_registered", False),
    })


def register(request):
    if request.method == "POST":
        name = " ".join(request.POST.get("name", "").split())
        raw = request.POST.get("mobile", "").strip()
        digits = re.sub(r"\D", "", raw)
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        elif len(digits) == 11 and digits.startswith("0"):
            digits = digits[1:]
        branch = request.POST.get("branch", "").strip().lower()
        valid_branches = {value for value, label in TYPING_BRANCHES}
        error = ""
        if not 2 <= len(name) <= 100:
            error = "Enter your name (2–100 characters)."
        elif not re.fullmatch(r"[6-9][0-9]{9}", digits):
            error = "Enter a valid 10-digit Indian mobile number."
        elif branch not in valid_branches:
            error = "Select your preferred centre."

        if error:
            return render(request, "typing_practice/public_register.html", {
                "branches": TYPING_BRANCHES, "error": error,
                "entered_name": name, "entered_mobile": raw,
                "entered_branch": branch,
            })

        recent = Enquiry.objects.filter(
            mobile=digits,
            message__icontains="MCTI Typing Lab",
        ).exists()
        if not recent:
            Enquiry.objects.create(
                name=name, mobile=digits, branch=branch,
                message=(
                    "MCTI Typing Lab - Free Public Registration. "
                    "Lead Source: Typing Practice."
                ),
                status="new",
            )
        request.session["typing_public_registered"] = True
        request.session["typing_public_name"] = name
        request.session["typing_public_mobile"] = digits
        request.session["typing_public_branch"] = branch
        return redirect("typing_practice:public_typing")

    return render(request, "typing_practice/public_register.html", {
        "branches": TYPING_BRANCHES,
    })


@require_POST
def save_progress(request):
    slug = request.POST.get("slug", "")
    lesson = next((x for x in LESSONS if x.slug == slug), None)
    if lesson is None:
        return JsonResponse({"error": "Invalid lesson."}, status=400)
    if lesson.order > 2 and not request.session.get("typing_public_registered"):
        return JsonResponse({"error": "Register to continue."}, status=403)
    try:
        seconds = int(request.POST.get("seconds", "0"))
        errors = int(request.POST.get("errors", "-1"))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid result."}, status=400)
    length = len(lesson.content)
    if not 1 <= seconds <= 86400 or not 0 <= errors <= length:
        return JsonResponse({"error": "Invalid result."}, status=400)

    accuracy = round((length-errors) * 100 / length, 1)
    wpm = round((length-errors) * 12 / seconds, 1)
    progress = dict(request.session.get("typing_free_progress", {}))
    progress[slug] = {"wpm": wpm, "accuracy": accuracy}
    request.session["typing_free_progress"] = progress
    # Guest practice results are not exam or certificate evidence.
    return JsonResponse({"saved": True})
