from django.db import models


class Repo(models.Model):
    github_full_name = models.CharField(max_length=255)

    def __str__(self):
        return self.github_full_name

