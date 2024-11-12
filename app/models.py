from django.db import models


class Repo(models.Model):
    nfkc_github_full_name = models.CharField(max_length=255)
    nfkc_clone_url = models.CharField(max_length=255)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.nfkc_github_full_name


class Analysis(models.Model):
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    analysis_result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis of {self.repo.nfkc_github_full_name}"
