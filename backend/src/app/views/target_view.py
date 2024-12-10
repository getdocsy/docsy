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


class TargetForm(forms.Form):
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "3",
                "placeholder": "Enter target description",
            }
        )
    )


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(login_required, name="dispatch")
class TargetView(View):
    template_name = "target.html"

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated
        form = TargetForm()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "is_authenticated": is_authenticated,
                "username": user.username,
            },
        )

    def post(self, request):
        user = request.user
        is_authenticated = user.is_authenticated
        form = TargetForm(request.POST)
        if form.is_valid():
            target = target_service.create_target(
                description=form.cleaned_data["description"],
            )
            form = TargetForm()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "is_authenticated": is_authenticated,
                "username": user.username,
            },
        )
