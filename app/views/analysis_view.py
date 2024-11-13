from django.http import HttpResponse

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
        if self.action == 'create':
            return GithubFullNameSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request):
        github_full_name = request.data.get('github_full_name')
        if not github_full_name:
            return HttpResponse("Missing required parameter: github_full_name", status=400)

        sanitized_github_full_name = sanitization_utils.strip_xss(
            unsafe_github_full_name=github_full_name
        )

        try:
            analysis_result = analysis_service.analyze_remote_repo(
                sanitized_github_full_name=sanitized_github_full_name
            )
            return HttpResponse(analysis_result)
        except custom_errors.PublicGithubRepoNotFoundError as e:
            return HttpResponse(str(e), status=404)
