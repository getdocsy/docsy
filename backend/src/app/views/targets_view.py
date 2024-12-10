from django.views.generic import View
from django.shortcuts import render, redirect
from django.db.models import QuerySet
from django.db.models.query import QuerySet
from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from app.models import Target, Repo
from django import forms
from django.contrib.auth.decorators import login_required
from app.services import target_service


@method_decorator(login_required, name="dispatch")
class TargetsView(View):
    template_name = "targets.html"

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated
        targets = target_service.get_all_targets()
        return render(
            request,
            self.template_name,
            {
                "is_authenticated": is_authenticated,
                "user": user,
                "targets": targets,
            },
        )
