from django.urls import path
from app.views.analysis_view import (
    AnalysisResultView,
    AnalysisFormView,
)
from app.api import github_api

urlpatterns = [
    path("analysis/result/", AnalysisResultView.as_view(), name="analysis-result"),
    path("analysis/", AnalysisFormView.as_view(), name="analysis_form"),
    path("github/", github_api.urls),
    path("", AnalysisFormView.as_view(), name="analysis_form"),
]
