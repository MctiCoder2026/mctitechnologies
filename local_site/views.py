from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Course, Enquiry
from .forms import LocalEnquiryForm
from .models import Branch


def branch_landing(request, slug):

    branch = get_object_or_404(
        Branch,
        slug=slug,
        is_active=True
    )

    testimonials = branch.testimonials.filter(
        is_active=True
    )

    gallery_images = branch.gallery_images.filter(
        is_active=True
    )

    popular_courses = Course.objects.filter(
        is_active=True,
        is_trending=True
    ).order_by("display_order")[:12]

    if request.method == "POST":

        form = LocalEnquiryForm(request.POST)

        if form.is_valid():

            Enquiry.objects.create(
                name=form.cleaned_data["name"],
                mobile=form.cleaned_data["mobile"],
                email=form.cleaned_data["email"],
                course=form.cleaned_data["course"],
                branch=branch.name,
                message=(
                    "Local Website Enquiry - "
                    + branch.name
                    + " Branch"
                    + (
                        "\n\n"
                        + form.cleaned_data["message"]
                        if form.cleaned_data["message"]
                        else ""
                    )
                ),
                status="new",
            )

            messages.success(
                request,
                "Thank you! Your enquiry has been submitted. Our counsellor will contact you shortly."
            )

            return redirect(branch.slug)

    else:
        form = LocalEnquiryForm()

    context = {
        "branch": branch,
        "testimonials": testimonials,
        "gallery_images": gallery_images,
        "popular_courses": popular_courses,
        "form": form,
    }

    return render(
        request,
        "local_site/branch_landing.html",
        context
    )




def local_home(request):
    branches = Branch.objects.filter(
        is_active=True
    ).order_by("name")

    popular_courses = Course.objects.filter(
        is_active=True,
        is_trending=True
    ).order_by("display_order")[:12]

    return render(
        request,
        "local_site/home.html",
        {
            "branches": branches,
            "popular_courses": popular_courses,
        }
    )
