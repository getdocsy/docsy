from django.http import HttpResponse

from app import custom_errors, sanitization_utils
from app.models import Analysis, Repo
from app.services import analysis_service

from rest_framework import viewsets, permissions
from app.serializers import AnalysisSerializer, RepoSerializer

class RepoViewSet(viewsets.ModelViewSet):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    permission_classes = [permissions.IsAuthenticated]

