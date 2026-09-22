from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Course
from local_site.models import Branch


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "about",
            "academy",
            "courses",
            "business_solutions",
            "ai",
            "saas",
            "contact",
            "privacy_policy",
            "terms_and_conditions",
            "refund_policy",
        ]

    def location(self, item):
        return reverse(item)


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Course.objects.filter(
            is_active=True
        ).exclude(
            slug=""
        )

    def location(self, obj):
        return reverse(
            "course_detail",
            kwargs={"slug": obj.slug}
        )
class BranchSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Branch.objects.filter(
            is_active=True
        ).exclude(
            slug=""
        )

    def location(self, obj):
        return reverse(obj.slug)


class LocalStaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["home"]

    def location(self, item):
        return reverse(item)
