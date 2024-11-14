from django.contrib import admin

from .models import Repo, Analysis


class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("repo", "created_at", "status")


admin.site.register(Repo)
admin.site.register(Analysis, AnalysisAdmin)
