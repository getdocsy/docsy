from django.urls import path, include
from django.contrib import admin
from app.views import analysis_view, repo_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
]
