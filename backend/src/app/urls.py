from django.urls import path
from django.contrib.auth import views as auth_views

from app.api import github_api
from app.views.analysis_view import (
    AnalysisResultView,
    AnalysisFormView,
)
from app.views.target_view import TargetView

urlpatterns = [
    path("github/", github_api.urls),
    path("analysis/result/", AnalysisResultView.as_view(), name="analysis-result"),
    path("analysis/", AnalysisFormView.as_view(), name="analysis_form"),
    path("target/", TargetView.as_view(), name="target"),
    path("", AnalysisFormView.as_view(), name="analysis_form"),
]
