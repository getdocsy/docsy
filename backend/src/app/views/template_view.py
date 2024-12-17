from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django import forms
from app.services import template_service


class TemplateForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    structure = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': '# Overview\nThis section provides a high-level summary.\n\n# Installation\nSteps to install the software.\n\n# Usage\nHow to use the main features.'
        })
    )


@method_decorator(login_required, name="dispatch")
class TemplateView(View):
    template_name = "template.html"
    
    def get(self, request):
        form = TemplateForm()
        return render(
            request,
            self.template_name,
            {
                "is_authenticated": request.user.is_authenticated,
                "user": request.user,
                "form": form,
            },
        )

    def post(self, request):
        form = TemplateForm(request.POST)
        if form.is_valid():
            template = template_service.create_template(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                structure=form.cleaned_data["structure"]
            )
            return redirect("templates")
        
        return render(
            request,
            self.template_name,
            {
                "is_authenticated": request.user.is_authenticated,
                "user": request.user,
                "form": form,
            },
        ) 