import json
from django.db import models
from django.contrib.auth import get_user_model


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, sort_keys=True, **kwargs)


class Repo(models.Model):
    nfkc_github_full_name = models.CharField(max_length=255)
    nfkc_clone_url = models.CharField(max_length=255)
    is_public = models.BooleanField(default=True)
    enable_pull_request_analysis = models.BooleanField(default=False)

    @property
    def owner(self):
        return self.nfkc_github_full_name.split("/")[0]

    @property
    def name(self):
        return self.nfkc_github_full_name.split("/")[1]

    def __str__(self):
        return self.nfkc_github_full_name


class Analysis(models.Model):

    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    result = models.JSONField(default=dict, encoder=PrettyJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis of {self.repo.nfkc_github_full_name}"


class RepoMap(models.Model):

    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    result = models.JSONField(default=dict, encoder=PrettyJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True)
    created_for_commit_sha = models.CharField(max_length=255)


class Target(models.Model):
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description


class Template(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    structure = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
