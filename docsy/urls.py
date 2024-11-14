from django.urls import path, include
from django.contrib import admin
from app.views import analysis_view, repo_view

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"analysis", analysis_view.AnalysisViewSet)
router.register(r"repo", repo_view.RepoViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("", include("app.urls")),
]
