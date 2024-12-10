from django.contrib import admin

from .models import Analysis, Repo, RepoMap, Target


class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("repo", "created_at")


class TargetAdmin(admin.ModelAdmin):
    list_display = ("description", "created_at")


admin.site.register(Repo)
admin.site.register(Analysis, AnalysisAdmin)
admin.site.register(RepoMap)
admin.site.register(Target, TargetAdmin)