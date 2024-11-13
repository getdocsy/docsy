from rest_framework import serializers

from app.models import Analysis, Repo

class AnalysisSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Analysis
        fields = ["url", "created_at", "repo", "analysis_result"]

class RepoSerializer(serializers.HyperlinkedModelSerializer):
    github_full_name = serializers.CharField(source='nfkc_github_full_name')
    clone_url = serializers.CharField(source='nfkc_clone_url')

    class Meta:
        model = Repo
        fields = ["url", "github_full_name", "clone_url", "is_public"]
