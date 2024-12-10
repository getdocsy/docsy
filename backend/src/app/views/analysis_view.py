from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from app import custom_errors
from app.services import analysis_service


class AnalysisView(View):
    template_name = "analysis/create.html"

    async def get(self, request):
        user = await request.auser()
        is_authenticated = user.is_authenticated
        return render(
            request,
            self.template_name,
            {"is_authenticated": is_authenticated, "user": user},
        )

    async def post(self, request):
        user = await request.auser()
        is_authenticated = user.is_authenticated
        github_full_name = request.POST.get("github_full_name")
        if not github_full_name:
            return render(
                request,
                self.template_name,
                {
                    "error": "GitHub repository name is required",
                    "is_authenticated": is_authenticated,
                    "user": user,
                },
            )

        try:
            await analysis_service.analyze_remote_repo(
                sanitized_github_full_name=github_full_name
            )
            owner, name = github_full_name.split("/")
            return redirect(f"{reverse('analysis-result')}?owner={owner}&name={name}")
        except custom_errors.PublicGithubRepoNotFoundError as e:
            return render(
                request,
                self.template_name,
                {
                    "error": str(e),
                    "is_authenticated": is_authenticated,
                    "user": user,
                },
            )


class AnalysisResultView(View):
    template_name = "analysis/result.html"

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
