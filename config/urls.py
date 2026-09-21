"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, CourseSitemap, BranchSitemap
from local_site.views import branch_landing

sitemaps = {
    "static": StaticViewSitemap,
    "courses": CourseSitemap,
    "branches": BranchSitemap,
}
urlpatterns = [
    path('kharghar/', branch_landing, {'slug': 'kharghar'}, name='kharghar'),
    path('panvel/', branch_landing, {'slug': 'panvel'}, name='panvel'),
    path('nerul/', branch_landing, {'slug': 'nerul'}, name='nerul'),
    path('ghansoli/', branch_landing, {'slug': 'ghansoli'}, name='ghansoli'),
    path('kamothe/', branch_landing, {'slug': 'kamothe'}, name='kamothe'),
    path('koperkhairane/', branch_landing, {'slug': 'koperkhairane'}, name='koperkhairane'),
    path('local/', include('local_site.urls')),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("lms/", include("lms.urls")),
    path("api/mobile/", include("mobile_api.urls")),
    path(
    "sitemap.xml",
    sitemap,
    {"sitemaps": sitemaps},
    name="django.contrib.sitemaps.views.sitemap",
    ),
]


# Serve uploaded media files during local development
if settings.DEBUG:
        urlpatterns += static(
            settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT
        )


