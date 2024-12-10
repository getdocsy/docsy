from django.urls import path, include
from django.contrib.auth import views as auth_views

from app.api import github_api
from app.views import (
    AnalysisView,
    AnalysisResultView,
    DashboardView,
    TargetView,
    FineTuningView,
)

urlpatterns = [
    path("github/", github_api.urls),
    path("analysis/result/", AnalysisResultView.as_view(), name="analysis-result"),
    path("analysis/", AnalysisView.as_view(), name="analysis"),
    path("target/", TargetView.as_view(), name="target"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("fine-tuning/", FineTuningView.as_view(), name="fine-tuning"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", AnalysisView.as_view()),
]
