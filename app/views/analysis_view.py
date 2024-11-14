from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from app import custom_errors, sanitization_utils
from app.models import Analysis, Repo
from app.services import analysis_service

from rest_framework import viewsets, permissions, serializers
from app.serializers import AnalysisSerializer, RepoSerializer


class GithubFullNameSerializer(serializers.Serializer):
    github_full_name = serializers.CharField(max_length=200)


class AnalysisViewSet(viewsets.ModelViewSet):
    queryset = Analysis.objects.filter(repo__is_public=True)
    serializer_class = AnalysisSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return GithubFullNameSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ["create", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request):
        unsafe_github_full_name = request.data.get("github_full_name")
        if not unsafe_github_full_name:
            return HttpResponse(
                "Missing required parameter: github_full_name", status=400
            )

        sanitized_github_full_name = sanitization_utils.strip_xss(
            unsafe_github_full_name=unsafe_github_full_name
        )

        try:
            analysis_service.analyze_remote_repo(
                sanitized_github_full_name=sanitized_github_full_name
            )
            owner, name = sanitized_github_full_name.split("/")
            return redirect(f"{reverse('analysis-result')}?owner={owner}&name={name}")
        except custom_errors.PublicGithubRepoNotFoundError as e:
            return HttpResponse(str(e), status=404)


class AnalysisFormView(View):
    template_name = "analysis/create.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        github_full_name = request.POST.get("github_full_name")
        if not github_full_name:
            return render(
                request,
                self.template_name,
                {"error": "GitHub repository name is required"},
            )

        sanitized_github_full_name = sanitization_utils.strip_xss(
            unsafe_github_full_name=github_full_name
        )

        try:
            analysis_service.analyze_remote_repo(
                sanitized_github_full_name=sanitized_github_full_name
            )
            owner, name = sanitized_github_full_name.split("/")
            return redirect(f"{reverse('analysis-result')}?owner={owner}&name={name}")
        except custom_errors.PublicGithubRepoNotFoundError as e:
            return render(request, self.template_name, {"error": str(e)})


class AnalysisResultView(View):
    template_name = "analysis/result.html"

    def get(self, request):
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
            },
        )


class AnalysisStatusView(View):
    def get(self, request):
        unsafe_owner = request.GET.get("owner")
        unsafe_name = request.GET.get("name")

        if not unsafe_owner or not unsafe_name:
            return JsonResponse(
                {"error": "Missing repository owner or name"}, status=400
            )

        sanitized_owner = sanitization_utils.strip_xss(unsafe_owner)
        sanitized_name = sanitization_utils.strip_xss(unsafe_name)

        sanitized_github_full_name = f"{sanitized_owner}/{sanitized_name}"
        analysis = analysis_service.get_latest_analysis_by_github_full_name(
            sanitized_github_full_name=sanitized_github_full_name
        )

        print(f"analysis status for {sanitized_github_full_name} requested")

        if not analysis:
            return JsonResponse({"error": "Analysis not found"}, status=404)

        return JsonResponse(
            {
                "status": analysis.status,
                "error": (
                    analysis.error_message
                    if hasattr(analysis, "error_message")
                    else None
                ),
            }
        )
