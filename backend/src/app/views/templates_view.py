from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from app.services import template_service


@method_decorator(login_required, name="dispatch")
class TemplatesView(View):
    template_name = "templates.html"

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated
        templates = template_service.get_all_templates()
        return render(
            request,
            self.template_name,
            {
                "is_authenticated": is_authenticated,
                "user": user,
                "templates": templates,
            },
        ) 