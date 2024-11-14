from django.contrib import admin

from .models import Repo, Analysis, RepoMap


class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("repo", "created_at")


admin.site.register(Repo)
admin.site.register(Analysis, AnalysisAdmin)
admin.site.register(RepoMap)
