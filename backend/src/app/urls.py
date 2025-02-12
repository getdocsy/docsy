from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.shortcuts import redirect
from django.views.generic import TemplateView

from app.api import github_api
from app.views import (
    AnalysisView,
    AnalysisResultView,
    DashboardView,
    TargetsView,
    TargetView,
    FineTuningView,
    IntegrationsView,
)
from app.views.repositories_view import RepositoriesView
from app.views.analysis_results_view import AnalysisResultsView
from app.views.target_details_view import TargetDetailsView
from app.views.templates_view import TemplatesView
from app.views.template_view import TemplateView
from app.views.template_details_view import TemplateDetailsView


@login_not_required
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("analysis")


urlpatterns = [
    path("github/", github_api.urls),
    path("analysis/result/", AnalysisResultView.as_view(), name="analysis-result"),
    path("analysis/", AnalysisView.as_view(), name="analysis"),
    path("targets/", TargetsView.as_view(), name="targets"),
    path("target/", TargetView.as_view(), name="target"),
    path("target/<int:target_id>/", TargetDetailsView.as_view(), name="target_detail"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("fine-tuning/", FineTuningView.as_view(), name="fine-tuning"),
    path("integrations/", IntegrationsView.as_view(), name="integrations"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("plausible/", TemplateView.as_view(template_name="plausible.html"), name="plausible"),
    path("repositories/", RepositoriesView.as_view(), name="repositories"),
    path("analysis/results/", AnalysisResultsView.as_view(), name="analysis-results"),
    path("templates/", TemplatesView.as_view(), name="templates"),
    path("template/", TemplateView.as_view(), name="template"),
    path("template/<int:template_id>/", TemplateDetailsView.as_view(), name="template_detail"),
    path("", root_redirect, name="root"),
]
