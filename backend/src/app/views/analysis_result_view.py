from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from app import custom_errors
from app.services import analysis_service


class AnalysisResultView(View):
    template_name = "analysis_result.html"

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated

        owner = request.GET.get("owner")
        name = request.GET.get("name")

        if not owner or not name:
            return HttpResponse("Missing repository owner or name", status=400)

        github_full_name = f"{owner}/{name}"
        analysis = analysis_service.get_latest_analysis_by_github_full_name(
            sanitized_github_full_name=github_full_name
        )

        if not analysis:
            return HttpResponse("Analysis not found", status=404)

        return render(
            request,
            self.template_name,
            {
                "result": analysis.result,
                "repo_owner": owner,
                "repo_name": name,
                "created_at": analysis.created_at,
                "is_authenticated": is_authenticated,
                "user": user,
            },
        )
