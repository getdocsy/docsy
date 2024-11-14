from django.urls import path
from app.views.analysis_view import (
    AnalysisStatusView,
    AnalysisResultView,
    AnalysisFormView,
)

urlpatterns = [
    path("analysis/status", AnalysisStatusView.as_view(), name="analysis-status"),
    path("analysis/result/", AnalysisResultView.as_view(), name="analysis-result"),
    path("analysis/", AnalysisFormView.as_view(), name="analysis_form"),
    path("", AnalysisFormView.as_view(), name="analysis_form"),
]
